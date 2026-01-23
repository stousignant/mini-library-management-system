<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useBookStore } from '@/stores/bookStore'
import { useAuthStore } from '@/stores/authStore'
import { useStatsStore } from '@/stores/statsStore'
import BookCard from './BookCard.vue'
import BookFormModal from './BookFormModal.vue'
import type { Book } from '@/types/Book'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { BookOpen, CheckCircle, Clock, Search, AlertCircle, Loader2, User } from 'lucide-vue-next'
import { Badge } from '@/components/ui/badge'

const bookStore = useBookStore()
const authStore = useAuthStore()
const statsStore = useStatsStore()
const isModalOpen = ref(false)
const bookToEdit = ref<Book | undefined>(undefined)

onMounted(() => {
  bookStore.filterUserId = authStore.user?.id || null
  bookStore.fetchBooks()
  statsStore.fetchStatistics()
  bookStore.startPolling()
  statsStore.startPolling()
})

onUnmounted(() => {
  bookStore.stopPolling()
  statsStore.stopPolling()
})

function openAddModal() {
  bookToEdit.value = undefined
  isModalOpen.value = true
}

function openEditModal(book: Book) {
  bookToEdit.value = book
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
  bookToEdit.value = undefined
}

async function handleSubmit(data: {
  title: string
  author: string
  isbn?: string
}) {
  try {
    if (bookToEdit.value) {
      await bookStore.updateBook(bookToEdit.value.id, data)
    } else {
      await bookStore.addBook(data)
    }
    await statsStore.fetchStatistics()
    closeModal()
  } catch (_err) {
    // Error already set in store
  }
}

async function handleDelete(bookId: number) {
  try {
    await bookStore.deleteBook(bookId)
    await statsStore.fetchStatistics()
  } catch (_err) {
    // Error already set in store
  }
}
</script>

<template>
  <div class="book-list space-y-6">
    <!-- Stats Dashboard -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Total Books</CardTitle>
          <BookOpen class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ statsStore.total }}</div>
          <p class="text-xs text-muted-foreground">
            Books in the library
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Available</CardTitle>
          <CheckCircle class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ statsStore.available }}</div>
          <p class="text-xs text-muted-foreground">
            Ready to borrow
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle class="text-sm font-medium">Borrowed</CardTitle>
          <Clock class="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div class="text-2xl font-bold">{{ statsStore.borrowed }}</div>
          <p class="text-xs text-muted-foreground">
            Currently out
          </p>
        </CardContent>
      </Card>
    </div>

    <!-- My Books Filter Button -->
    <div v-if="authStore.isAuthenticated" class="flex justify-center">
      <Button
        :variant="bookStore.showMyBooksOnly ? 'default' : 'outline'"
        size="lg"
        class="gap-2"
        @click="() => {
          bookStore.filterUserId = authStore.user?.id || null
          bookStore.showMyBooksOnly = !bookStore.showMyBooksOnly
        }"
      >
        <User class="h-5 w-5" />
        <span class="font-semibold">
          {{ bookStore.showMyBooksOnly ? 'Show All Books' : 'Show My Books' }}
        </span>
        <Badge
          :variant="bookStore.showMyBooksOnly ? 'secondary' : 'default'"
          class="ml-1"
        >
          {{ bookStore.myBorrowedCount }}
        </Badge>
      </Button>
    </div>

    <!-- Loading State -->
    <div
      v-if="bookStore.isLoading"
      data-testid="loading-state"
      class="flex items-center justify-center py-12"
    >
      <div class="text-center">
        <Loader2 class="inline-block h-12 w-12 animate-spin text-muted-foreground mb-4" />
        <p class="text-muted-foreground">Loading books...</p>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="bookStore.error"
      data-testid="error-state"
      class="bg-destructive/10 border border-destructive/20 rounded-lg p-4 text-destructive"
    >
      <AlertCircle class="inline-block w-5 h-5 mr-2" />
      {{ bookStore.error }}
    </div>

    <!-- Book List -->
    <div v-else data-testid="book-list" class="space-y-6">
      <div class="flex gap-4">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            v-model="bookStore.searchQuery"
            type="text"
            placeholder="Search by title or author..."
            class="pl-10"
            data-testid="search-input"
          />
        </div>
        <Button
          v-if="authStore.isAdmin"
          data-testid="add-book-btn"
          @click="openAddModal"
        >
          Add Book
        </Button>
      </div>

      <div
        v-if="bookStore.filteredBooks.length === 0"
        class="text-center py-12 text-muted-foreground"
      >
        <BookOpen class="mx-auto h-12 w-12 mb-4 opacity-50" />
        <p class="text-lg font-medium">
          {{
            bookStore.searchQuery
              ? 'No books match your search'
              : 'No books found'
          }}
        </p>
        <p class="text-sm mt-1">
          {{
            bookStore.searchQuery
              ? 'Try a different search term'
              : 'Add your first book to get started'
          }}
        </p>
      </div>

      <div
        v-else
        class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4"
      >
        <BookCard
          v-for="book in bookStore.filteredBooks"
          :key="book.id"
          :book="book"
          @edit="openEditModal"
          @delete="handleDelete"
        />
      </div>
    </div>

    <BookFormModal
      :is-open="isModalOpen"
      :book-to-edit="bookToEdit"
      @close="closeModal"
      @submit="handleSubmit"
    />
  </div>
</template>
