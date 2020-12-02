export interface WerkitMeta {
  start_time: string
  duration_seconds: number
  runtime_info?: any
}

export interface WerkitSuccessResult<ResultType> extends WerkitMeta {
  success: true
  result: ResultType
  error: null
  error_origin: null
}

export type WerkitErrorOrigin = 'compute' | 'system' | 'orchestration'

export interface WerkitErrorResult extends WerkitMeta {
  success: false
  result: null
  error: string[]
  error_origin: WerkitErrorOrigin
}

export type WerkitResult<ResultType> =
  | WerkitSuccessResult<ResultType>
  | WerkitErrorResult
