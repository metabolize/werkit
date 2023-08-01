export interface DestinationMessage<PayloadType> {
  taskIdentifier: string
  payload: PayloadType
}
