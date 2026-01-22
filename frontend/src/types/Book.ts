export enum BookStatus {
  Available = "available",
  Borrowed = "borrowed"
}

export interface Book {
  id: number
  title: string
  author: string
  isbn: string | null
  status: BookStatus
  created_at: string
}
