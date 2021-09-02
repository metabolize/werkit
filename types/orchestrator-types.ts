import { WerkitOutputMessage } from './werkit-types'

export interface OrchestratorInput<
  WorkerInputType,
  ItemPropertyName extends keyof WorkerInputType
> {
  itemPropertyName: ItemPropertyName
  itemCollection: Record<string, WorkerInputType[ItemPropertyName]>
  commonInput: Omit<WorkerInputType, ItemPropertyName>
}

export type OrchestratorOutput<WorkerOutputType, MessageKeyType> = Record<
  string,
  {
    startTimestamp: number
    roundtripSeconds: number
    output: WerkitOutputMessage<WorkerOutputType, MessageKeyType>
  }
>

export type OrchestratedWorkerInput<WorkerInputType> = {
  itemKey: string
} & WorkerInputType
