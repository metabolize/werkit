import { expect } from 'chai'

import {
  DependencyGraph,
  DependencyGraphWithBuiltInTypes,
} from './dependency-graph.schema'
import { generateComputeNodeInterfaces } from './generate-compute-node-interfaces'

const DEPENDENCY_GRAPH_WITH_BUILT_IN_TYPES: DependencyGraphWithBuiltInTypes = {
  schemaVersion: 1,
  inputs: {
    a: { valueType: 'number' },
    b: { valueType: 'number' },
  },
  intermediates: {
    i: { valueType: 'number', dependencies: ['a'] },
    j: { valueType: 'number', dependencies: ['b'] },
  },
  outputs: {
    r: { valueType: 'number', dependencies: ['i', 'j'] },
  },
}

const INTERFACE_FOR_DEPENDENCY_GRAPH_WITH_BUILT_IN_TYPES = `export interface InputNodes {
  a: number
  b: number
}

export interface IntermediateNodes {
  i: number
  j: number
}

export interface OutputNodes {
  r: number
}
`

type ValueType = 'number' | 'MyModel'

const DEPENDENCY_GRAPH_WITH_CUSTOM_TYPE: DependencyGraph<ValueType> = {
  schemaVersion: 1,
  inputs: {
    a: { valueType: 'number' },
    b: { valueType: 'number' },
  },
  intermediates: {
    i: { valueType: 'MyModel', dependencies: ['a'] },
    j: { valueType: 'MyModel', dependencies: ['b'] },
  },
  outputs: {
    r: { valueType: 'MyModel', dependencies: ['i', 'j'] },
  },
}

const INTERFACE_FOR_DEPENDENCY_GRAPH_WITH_CUSTOM_TYPE = `import { MyModel } from '../models'

export interface InputNodes {
  a: number
  b: number
}

export interface IntermediateNodes {
  i: MyModel
  j: MyModel
}

export interface OutputNodes {
  r: MyModel
}
`

describe('`generateComputeNodeTypes()`', () => {
  context('given a dependency graph using built-in types', () => {
    it('generates the expected interfaces', () => {
      expect(
        generateComputeNodeInterfaces({
          dependencyGraph: DEPENDENCY_GRAPH_WITH_BUILT_IN_TYPES,
        }),
      ).to.equal(INTERFACE_FOR_DEPENDENCY_GRAPH_WITH_BUILT_IN_TYPES)
    })
  })

  context('given a dependency graph using a custom type', () => {
    it('generates the expected interfaces', () => {
      expect(
        generateComputeNodeInterfaces({
          dependencyGraph: DEPENDENCY_GRAPH_WITH_CUSTOM_TYPE,
          imports: "import { MyModel } from '../models'",
        }),
      ).to.equal(INTERFACE_FOR_DEPENDENCY_GRAPH_WITH_CUSTOM_TYPE)
    })
  })
})
