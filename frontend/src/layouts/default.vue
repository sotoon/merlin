<template>
  <div class="flex min-h-screen bg-gray-00">
    <aside class="sticky top-0 h-screen">
      <Sidebar />
    </aside>

    <main class="flex min-h-screen grow justify-center md:p-5 lg:px-6 lg:py-10">
      <div class="container h-full">
        <slot />
      </div>
    </main>
  </div>
</template>
