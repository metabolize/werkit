export type BuiltInValueType = 'Boolean' | 'Number' | 'String'

export interface Input<ValueType extends BuiltInValueType> {
  valueType: ValueType
}

export interface InnerNode<ValueType extends BuiltInValueType> {
  valueType: ValueType
  dependencies: string[]
}

export interface DependencyGraph<ValueType extends BuiltInValueType> {
  schemaVersion: 1
  inputs: { [k: string]: Input<ValueType> }
  intermediates: { [k: string]: InnerNode<ValueType> }
  outputs: { [k: string]: InnerNode<ValueType> }
}
