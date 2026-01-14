export type WerkitInputMessage<InputType, MessageKeyType> = {
  message_key: MessageKeyType
} & InputType

export interface WerkitComputeMeta {
  start_time: string
  duration_seconds: number
  runtime_info?: any
}

export interface WerkitSuccessOutputMessage<
  ResultType,
  MessageKeyType,
> extends WerkitComputeMeta {
  success: true
  result: ResultType
  error: null
  error_origin: null
  message_key: MessageKeyType
}

export type WerkitErrorOrigin = 'compute' | 'system' | 'orchestration'

export interface WerkitErrorOutputMessage<
  MessageKeyType,
> extends WerkitComputeMeta {
  success: false
  result: null
  error: string[]
  error_origin: WerkitErrorOrigin
  message_key: MessageKeyType
}

export type WerkitOutputMessage<ResultType, MessageKeyType> =
  | WerkitSuccessOutputMessage<ResultType, MessageKeyType>
  | WerkitErrorOutputMessage<MessageKeyType>

export type AnyWerkitOutputMessage = WerkitOutputMessage<any, any>
