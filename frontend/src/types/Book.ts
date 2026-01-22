export enum BookStatus {
  Available = 'AVAILABLE',
  Borrowed = 'BORROWED',
}

export interface Book {
  id: number
  title: string
  author: string
  isbn: string | null
  status: BookStatus
  created_at: string
}
