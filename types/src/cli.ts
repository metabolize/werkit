#!/usr/bin/env ts-node-script

'use strict'

import { promises as fs } from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { ArgumentParser } from 'argparse'
import { generateComputeNodeInterfaces } from './generate-compute-node-interfaces.js'

async function performGenerateComputeNodeInterfaces({
  dependencyGraphPath,
  importPath,
}: {
  dependencyGraphPath: string
  importPath?: string
}): Promise<void> {
  const dependencyGraph = JSON.parse(
    await fs.readFile(dependencyGraphPath, 'utf-8'),
  )
  // TODO: Validate using the JSON schema.

  let imports: string | undefined = undefined
  if (importPath) {
    imports = await fs.readFile(importPath, 'utf-8')
  }

  console.log(generateComputeNodeInterfaces({ dependencyGraph, imports }))
}

export default async function main(inArgs?: string[]): Promise<void> {
  const { description, version } = JSON.parse(
    await fs.readFile(
      path.join(
        path.dirname(fileURLToPath(import.meta.url)),
        '..',
        'package.json',
      ),
      'utf-8',
    ),
  )

  const parser = new ArgumentParser({
    prog: 'werkit',
    description,
  })
  parser.add_argument('-v', '--version', { action: 'version', version })

  const subparsers = parser.add_subparsers({
    dest: 'command',
    title: 'subcommands',
    description: 'valid subcommands',
    required: true,
  })
  const interfaceParser = subparsers.add_parser('interfaces', {
    help: 'Generate TypeScript interfaces for a dependency graph',
  })
  interfaceParser.add_argument('dependencyGraph', {
    help: 'Path to a JSON file containing the dependency graph',
    metavar: 'DEPENDENCY_GRAPH',
  })
  interfaceParser.add_argument('--imports', {
    help: 'Path to a TypeScript file containing imports, which are prepended to the output',
  })

  const args = parser.parse_args(inArgs)

  switch (args.command) {
    case 'interfaces':
      await performGenerateComputeNodeInterfaces({
        dependencyGraphPath: args.dependencyGraph,
        importPath: args.imports,
      })
      break
    default:
      throw Error(`Unknown command: ${args.command}`)
  }
}

;(async (): Promise<void> => {
  try {
    await main()
  } catch (e) {
    // eslint-disable-next-line no-console
    console.error(e)
    process.exit(1)
  }
})()
