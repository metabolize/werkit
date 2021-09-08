import { WerkitInputMessage, WerkitOutputMessage } from 'werkit'

export interface Input {
  base: number
  exponent: number
}

export type Output = number

export type InputMessage<MessageKeyType> = WerkitInputMessage<
  Input,
  MessageKeyType
>
export type OutputMessage<MessageKeyType> = WerkitOutputMessage<
  Output,
  MessageKeyType
>
export type AnyInputMessage = InputMessage<any>
export type AnyOutputMessage = OutputMessage<any>
