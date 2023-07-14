// @ts-ignore
import uuidToHex from '@metabolize/uuid-to-hex'
import { v4 as uuidv4 } from 'uuid'

export function uuidHex(): string {
  return uuidToHex(uuidv4())
}
