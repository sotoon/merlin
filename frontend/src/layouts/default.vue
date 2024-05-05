<template>
  <div class="flex min-h-screen bg-gray-00">
    <aside class="sticky top-0 h-screen bg-white shadow-lg">
      <div class="hidden h-full md:block">
        <Sidebar />
      </div>

      <div class="h-full md:hidden">
        <SidebarMobile />
      </div>
    </aside>

    <main
      class="flex min-h-screen min-w-0 grow justify-center md:p-5 lg:px-6 lg:py-10"
    >
      <div class="container h-full">
        <slot />
      </div>
    </main>
  </div>
</template>
