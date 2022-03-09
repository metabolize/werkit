import { BuiltInValueType } from './schema'

export type ValueType = BuiltInValueType | 'Point' | 'Measurement'

export type Vector3 = [number, number, number]
export type Point = Vector3

export type LengthUnits = 'mm' | 'cm' | 'm'
export type AngleUnits = 'deg'
export interface Polyline {
  vertices: Vector3[]
  is_closed: boolean
}

export interface Measurement {
  indicator: Polyline
  value: number
  units: LengthUnits | AngleUnits
}
