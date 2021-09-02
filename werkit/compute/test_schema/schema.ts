import { WerkitRequest, WerkitResult } from 'werkit'

export interface Input {
  label: string
  message: string
}

export interface Output {
  someString: string
  someNumber: number
}

export type RequestMessage<MessageKeyType> = WerkitRequest<Input, MessageKeyType>
export type ResponseMessage<MessageKeyType> = WerkitResult<Output, MessageKeyType>
export type AnyRequestMessage = RequestMessage<any>
export type AnyResponseMessage = ResponseMessage<any>
