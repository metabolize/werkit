import {
  WerkitInputMessage,
  WerkitOutputMessage,
  OrchestratorOutput,
} from 'werkit'

// Since the orchestrator is agnostic to the specific interface of the worker,
// it can't fully validate its input (at least not using JSON Schema) according
// to the `OrchestratorInput` type exported from `werkit`. Instead, this more
// permissinve type definition is used.
export interface Input {
  itemPropertyName: string
  commonInput: any
  itemCollection: Record<string, any>
}

export type InputMessage<MessageKeyType> = WerkitInputMessage<
  Input,
  MessageKeyType
>

export type Output<WorkerOutputType, MessageKeyType> = OrchestratorOutput<
  WorkerOutputType,
  MessageKeyType
>

export type OutputMessage<WorkerOutputType, MessageKeyType> =
  WerkitOutputMessage<
    OrchestratorOutput<WorkerOutputType, MessageKeyType>,
    MessageKeyType
  >

export type AnyInputMessage = InputMessage<any>
export type AnyOutput = Output<any, any>
export type AnyOutputMessage = OutputMessage<any, any>
