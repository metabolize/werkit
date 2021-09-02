import { WerkitRequest, WerkitResult } from 'werkit'

export interface Input {
  label: string
  message: string
}

export interface Output {
  someString: string
  someNumber: number
}

export type InputMessage<MessageKeyType> = WerkitRequest<Input, MessageKeyType>
export type OutputMessage<MessageKeyType> = WerkitResult<Output, MessageKeyType>
export type AnyInputMessage = InputMessage<any>
export type AnyOutputMessage = OutputMessage<any>
