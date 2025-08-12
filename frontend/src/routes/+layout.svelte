<script>
	import '../app.css';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	
	// Auth state
	let isAuthenticated = false;
	let currentUser = null;
	let loading = true;
	
	// Handle params prop to avoid warning
	export const data = {};
	
	onMount(async () => {
		// Check authentication status
		await checkAuth();
	});
	
	async function checkAuth() {
		try {
			const response = await fetch('/api/auth/check', {
				credentials: 'include'
			});
			
			if (response.ok) {
				const data = await response.json();
				isAuthenticated = data.authenticated;
				currentUser = data.user;
				
				// If not authenticated and not on login page, redirect to login
				if (!isAuthenticated && window.location.pathname !== '/login') {
					goto('/login');
				}
			} else {
				// If auth check fails and not on login page, redirect to login
				if (window.location.pathname !== '/login') {
					goto('/login');
				}
			}
		} catch (error) {
			console.error('Auth check failed:', error);
			// If auth check fails and not on login page, redirect to login
			if (window.location.pathname !== '/login') {
				goto('/login');
			}
		} finally {
			loading = false;
		}
	}
	
	async function logout() {
		try {
			await fetch('/api/auth/logout', {
				method: 'POST',
				credentials: 'include'
			});
			
			isAuthenticated = false;
			currentUser = null;
			goto('/login');
		} catch (error) {
			console.error('Logout failed:', error);
		}
	}
</script>

<svelte:head>
	<title>Internal Assistant</title>
</svelte:head>

{#if loading}
	<!-- Loading state -->
	<div class="min-h-screen bg-gray-50 flex items-center justify-center">
		<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
	</div>
{:else if isAuthenticated}
	<!-- Main Layout -->
	<div class="min-h-screen bg-gray-50">
		<div class="flex min-h-screen">
			<!-- Sidebar -->
			<aside class="w-64 bg-white border-r border-gray-200 flex flex-col">
				<!-- Header -->
				<div class="p-4 border-b border-gray-200">
					<h1 class="text-xl font-semibold text-gray-900">Internal Assistant</h1>
					{#if currentUser}
						<p class="text-sm text-gray-600 mt-1">{currentUser.email}</p>
						<p class="text-xs text-gray-500 capitalize">{currentUser.role}</p>
					{/if}
				</div>
				
				<!-- Navigation -->
				<nav class="flex-1 p-4">
					<ul class="space-y-2">
						<li>
							<a href="/" class="flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-md hover:bg-gray-100">
								Dashboard
							</a>
						</li>
						<li>
							<a href="/integrations" class="flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-md hover:bg-gray-100">
								Integrations
							</a>
						</li>
						<li>
							<a href="/chat" class="flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-md hover:bg-gray-100">
								Chat
							</a>
						</li>
						<li>
							<a href="/documents" class="flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-md hover:bg-gray-100">
								Documents
							</a>
						</li>
					</ul>
				</nav>
				
				<!-- Footer -->
				<div class="p-4 border-t border-gray-200">
					<button 
						on:click={logout}
						class="w-full px-3 py-2 text-sm font-medium text-gray-700 rounded-md hover:bg-gray-100"
					>
						Logout
					</button>
				</div>
			</aside>
			
			<!-- Main Content -->
			<main class="flex-1 overflow-auto">
				<slot />
			</main>
		</div>
	</div>
{:else}
	<!-- Login/Auth Pages -->
	<slot />
{/if}
