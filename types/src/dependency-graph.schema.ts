export type BuiltInValueType = 'boolean' | 'number' | 'string'

export interface Input<ValueType extends string = BuiltInValueType> {
  valueType: ValueType
}

export interface ComputeNode<ValueType extends string = BuiltInValueType> {
  valueType: ValueType
  dependencies: string[]
}

export interface DependencyGraph<ValueType extends string = BuiltInValueType> {
  schemaVersion: 1
  inputs: { [k: string]: Input<ValueType> }
  intermediates: { [k: string]: ComputeNode<ValueType> }
  outputs: { [k: string]: ComputeNode<ValueType> }
}

// When defining custom types, callers can extend BuiltInValueType:
// export type ValueType = BuiltInValueType | 'MyThing' | 'MyOtherThing'
// export typy MyDependencyGraph = DependencyGraph<ValueType>

export type DependencyGraphWithBuiltInTypes = DependencyGraph<BuiltInValueType>
export type DependencyGraphWithAnyTypes = DependencyGraph<string>
