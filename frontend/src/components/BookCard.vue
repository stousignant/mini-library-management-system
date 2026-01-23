<script setup lang="ts">
import type { Book } from '@/types/Book'
import { BookStatus } from '@/types/Book'
import { useBookStore } from '@/stores/bookStore'
import { useAuthStore } from '@/stores/authStore'
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { User, BookOpen, Clock } from 'lucide-vue-next'

const props = defineProps<{
  book: Book
}>()

const emit = defineEmits<{
  edit: [book: Book]
  delete: [bookId: number]
}>()

const bookStore = useBookStore()
const authStore = useAuthStore()

const getStatusVariant = (status: BookStatus) => {
  return status === BookStatus.Available ? 'default' : 'secondary'
}

const getButtonVariant = (status: BookStatus) => {
  return status === BookStatus.Available ? 'default' : 'secondary'
}

const getButtonLabel = (status: BookStatus) => {
  return status === BookStatus.Available ? 'Borrow' : 'Return'
}

function handleDelete() {
  if (
    window.confirm(`Are you sure you want to delete "${props.book.title}"?`)
  ) {
    emit('delete', props.book.id)
  }
}

function handleImageError(event: globalThis.Event) {
  const target = event.target as globalThis.HTMLImageElement
  target.style.display = 'none'
}
</script>

<template>
  <Card
    :data-testid="`book-item-${book.id}`"
    class="flex flex-col h-full"
  >
    <div class="relative w-full h-64 bg-muted">
      <div
        v-if="book.cover_image"
        class="w-full h-full flex items-center justify-center overflow-hidden"
      >
        <img
          :src="book.cover_image"
          :alt="`Cover of ${book.title}`"
          class="h-full w-full object-contain"
          @error="handleImageError"
        />
      </div>
      <div
        v-else
        class="w-full h-full bg-gradient-to-br from-muted to-muted/50 flex items-center justify-center"
      >
        <BookOpen class="w-16 h-16 text-muted-foreground" />
      </div>
      <Badge
        :variant="getStatusVariant(book.status)"
        class="absolute top-2 right-2 shadow-md"
      >
        {{ book.status }}
      </Badge>
    </div>

    <CardHeader>
      <h3
        class="text-lg font-bold text-foreground line-clamp-2"
        :title="book.title"
      >
        {{ book.title }}
      </h3>
    </CardHeader>

    <CardContent class="flex-1 space-y-2">
      <div class="flex items-center text-sm text-muted-foreground">
        <User class="w-4 h-4 mr-2" />
        <span class="font-medium">{{ book.author }}</span>
      </div>

      <div class="flex items-center text-sm text-muted-foreground">
        <BookOpen class="w-4 h-4 mr-2" />
        <span>{{ book.isbn || 'No ISBN' }}</span>
      </div>

      <div
        v-if="book.summary"
        class="pt-2 text-sm text-muted-foreground italic border-t"
      >
        {{ book.summary }}
      </div>

      <div
        class="flex items-center text-xs text-muted-foreground pt-2 border-t"
      >
        <Clock class="w-4 h-4 mr-1" />
        Added {{ new Date(book.created_at).toLocaleDateString() }}
      </div>
    </CardContent>

    <CardFooter class="flex-col gap-2">
      <Button
        v-if="authStore.isAuthenticated"
        :variant="getButtonVariant(book.status)"
        class="w-full"
        data-testid="toggle-status-btn"
        @click="bookStore.toggleStatus(book.id)"
      >
        {{ getButtonLabel(book.status) }}
      </Button>

      <div v-if="authStore.isAdmin" class="flex w-full gap-2">
        <Button
          variant="outline"
          class="flex-1"
          data-testid="edit-btn"
          @click="emit('edit', book)"
        >
          Edit
        </Button>
        <Button
          variant="outline"
          class="flex-1 text-destructive hover:text-destructive"
          data-testid="delete-btn"
          @click="handleDelete"
        >
          Delete
        </Button>
      </div>
    </CardFooter>
  </Card>
</template>
