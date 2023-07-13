import { DependencyGraph } from './dependency-graph.schema'

const INPUT_NODES_NAME = 'InputNodes'
const INTERMEDIATE_NODES_NAME = 'IntermediateNodes'
const OUTPUT_NODES_NAME = 'OutputNodes'

export function generateComputeNodeTypes<ValueType extends string>({
  dependencyGraph,
  imports,
}: {
  dependencyGraph: DependencyGraph<ValueType>
  imports?: string
}): string {
  const interfaces = `\
export interface ${INPUT_NODES_NAME} {
  ${Object.entries(dependencyGraph.inputs)
    .map(([k, v]) => `${k}: ${v.valueType}`)
    .join('\n  ')}
}

export interface ${INTERMEDIATE_NODES_NAME} {
  ${Object.entries(dependencyGraph.intermediates)
    .map(([k, v]) => `${k}: ${v.valueType}`)
    .join('\n  ')}
}

export interface ${OUTPUT_NODES_NAME} {
  ${Object.entries(dependencyGraph.outputs)
    .map(([k, v]) => `${k}: ${v.valueType}`)
    .join('\n  ')}
}
`
  return [imports, interfaces].filter(Boolean).join('\n\n')
}
