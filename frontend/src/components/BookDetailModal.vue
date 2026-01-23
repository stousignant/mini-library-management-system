<script setup lang="ts">
import type { Book } from '@/types/Book'
import { BookStatus } from '@/types/Book'
import { useBookStore } from '@/stores/bookStore'
import { useAuthStore } from '@/stores/authStore'
import { computed } from 'vue'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { User, BookOpen, Clock, Hash } from 'lucide-vue-next'

const props = defineProps<{
  isOpen: boolean
  book: Book | null
}>()

const emit = defineEmits<{
  close: []
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
  if (!props.book || !authStore.isAuthenticated) {
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

function handleImageError(event: globalThis.Event) {
  const target = event.target as globalThis.HTMLImageElement
  target.style.display = 'none'
}

function handleClose() {
  emit('close')
}
</script>

<template>
  <Dialog :open="isOpen" @update:open="handleClose">
    <DialogContent class="max-w-3xl max-h-[90vh] overflow-y-auto">
      <DialogHeader v-if="book">
        <DialogTitle class="text-2xl font-bold pr-8">
          {{ book.title }}
        </DialogTitle>
        <DialogDescription class="flex items-center gap-2 pt-2">
          <Badge :variant="getStatusVariant(book.status)">
            {{ book.status }}
          </Badge>
        </DialogDescription>
      </DialogHeader>

      <div v-if="book" class="space-y-6">
        <!-- Cover Image -->
        <div class="w-full h-80 bg-muted rounded-lg overflow-hidden">
          <div
            v-if="book.cover_image"
            class="w-full h-full flex items-center justify-center"
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
            <BookOpen class="w-24 h-24 text-muted-foreground" />
          </div>
        </div>

        <!-- Book Details -->
        <div class="space-y-4">
          <div class="flex items-center text-base">
            <User class="w-5 h-5 mr-3 text-muted-foreground flex-shrink-0" />
            <div>
              <span class="text-sm text-muted-foreground">Author</span>
              <p class="font-medium">{{ book.author }}</p>
            </div>
          </div>

          <div v-if="book.isbn" class="flex items-center text-base">
            <Hash class="w-5 h-5 mr-3 text-muted-foreground flex-shrink-0" />
            <div>
              <span class="text-sm text-muted-foreground">ISBN</span>
              <p class="font-medium">{{ book.isbn }}</p>
            </div>
          </div>

          <div class="flex items-center text-base">
            <Clock class="w-5 h-5 mr-3 text-muted-foreground flex-shrink-0" />
            <div>
              <span class="text-sm text-muted-foreground">Added</span>
              <p class="font-medium">
                {{ new Date(book.created_at).toLocaleDateString() }}
              </p>
            </div>
          </div>

          <!-- Summary -->
          <div v-if="book.summary" class="pt-4 border-t">
            <h4 class="text-sm font-semibold text-muted-foreground mb-2">
              Summary
            </h4>
            <p class="text-base leading-relaxed whitespace-pre-wrap">
              {{ book.summary }}
            </p>
          </div>
        </div>

        <!-- Action Button -->
        <div class="pt-4 border-t">
          <Button
            v-if="canInteractWithBook"
            :variant="getButtonVariant(book.status)"
            class="w-full"
            @click="bookStore.toggleStatus(book.id)"
          >
            {{ getButtonLabel(book.status) }}
          </Button>
        </div>
      </div>
    </DialogContent>
  </Dialog>
</template>
