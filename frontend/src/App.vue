<script setup lang="ts">
import BookList from './components/BookList.vue'
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 py-6">
        <h1 class="text-3xl font-bold text-gray-900">
          Library Management System
        </h1>
      </div>
    </header>
    <main class="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
      <div class="mb-6">
        <h2 class="text-2xl font-semibold text-gray-800">Book Collection</h2>
        <p class="text-gray-600 mt-1">Browse and manage your library books</p>
      </div>
      <BookList />
    </main>
  </div>
</template>
