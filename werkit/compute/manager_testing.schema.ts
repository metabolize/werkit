import { WerkitInputMessage, WerkitOutputMessage } from 'werkit'

export interface Input {
  label: string
  message: string
}

export interface Output {
  someString: string
  someNumber: number
}

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
