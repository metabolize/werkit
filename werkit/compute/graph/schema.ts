export type ValueType = 'Number' | 'Point' | 'Measurement'

export interface Input {
  valueType: ValueType
}

export interface InnerNode {
  valueType: ValueType
  dependencies: string[]
}

export interface DependencyGraph {
  schemaVersion: 1
  inputs: { [k: string]: Input }
  intermediates: { [k: string]: InnerNode }
  outputs: { [k: string]: InnerNode }
}
