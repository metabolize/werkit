export type WerkitRequest<
  RequestOptionsType,
  MessageKeyType
> = RequestOptionsType & {
  message_key: MessageKeyType
}

export interface WerkitMeta {
  start_time: string
  duration_seconds: number
  runtime_info?: any
}

export interface WerkitSuccessResult<ResultType, MessageKeyType>
  extends WerkitMeta {
  success: true
  result: ResultType
  error: null
  error_origin: null
  message_key: MessageKeyType
}

export type WerkitErrorOrigin = 'compute' | 'system' | 'orchestration'

export interface WerkitErrorResult<MessageKeyType> extends WerkitMeta {
  success: false
  result: null
  error: string[]
  error_origin: WerkitErrorOrigin
  message_key: MessageKeyType
}

export type WerkitResult<ResultType, MessageKeyType> =
  | WerkitSuccessResult<ResultType, MessageKeyType>
  | WerkitErrorResult<MessageKeyType>
