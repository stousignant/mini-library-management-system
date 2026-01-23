<script setup lang="ts">
import { computed } from 'vue'
import type { Book } from '@/types/Book'
import { BookStatus } from '@/types/Book'
import { useBookStore } from '@/stores/bookStore'
import { useAuthStore } from '@/stores/authStore'
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
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
  return status === BookStatus.Available ? 'success' : 'warning'
}

const getButtonVariant = (status: BookStatus) => {
  return status === BookStatus.Available ? 'default' : 'secondary'
}

const getButtonLabel = (status: BookStatus) => {
  return status === BookStatus.Available ? 'Borrow' : 'Return'
}

const canInteractWithBook = computed(() => {
  if (!authStore.isAuthenticated) {
    return false
  }

  const statusStr = String(props.book.status).toUpperCase()
  const isAvailable = statusStr === 'AVAILABLE'
  if (isAvailable) {
    return true
  }

  const isBorrowed = statusStr === 'BORROWED'
  if (isBorrowed) {
    if (authStore.isAdmin) {
      return true
    }
    return props.book.borrowed_by === authStore.user?.id
  }

  return false
})

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
  <Card :data-testid="`book-item-${book.id}`" class="flex flex-col h-[660px]">
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

    <CardHeader class="h-[96px] pb-2">
      <h3
        class="text-lg font-bold text-foreground line-clamp-2"
        :title="book.title"
      >
        {{ book.title }}
      </h3>
    </CardHeader>

    <CardContent class="flex flex-col flex-grow">
      <div class="flex items-center text-sm text-muted-foreground h-6 mb-2">
        <User class="w-4 h-4 mr-2 flex-shrink-0" />
        <span class="font-medium truncate" :title="book.author">{{
          book.author
        }}</span>
      </div>

      <div class="flex items-center text-sm text-muted-foreground h-6 mb-2">
        <BookOpen class="w-4 h-4 mr-2 flex-shrink-0" />
        <span class="truncate" :title="book.isbn || 'No ISBN'">{{
          book.isbn || 'No ISBN'
        }}</span>
      </div>

      <div
        class="pt-2 text-sm text-muted-foreground italic border-t h-[84px] overflow-hidden mb-2"
        :title="book.summary || ''"
      >
        <p v-if="book.summary" class="line-clamp-3">
          {{ book.summary }}
        </p>
      </div>

      <div
        class="flex items-center text-xs text-muted-foreground pt-2 border-t h-6"
      >
        <Clock class="w-4 h-4 mr-1 flex-shrink-0" />
        <span class="truncate"
          >Added {{ new Date(book.created_at).toLocaleDateString() }}</span
        >
      </div>
    </CardContent>

    <CardFooter class="flex-col gap-2 mt-auto">
      <Button
        v-if="canInteractWithBook"
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
