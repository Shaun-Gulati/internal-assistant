<script>
	import { goto } from '$app/navigation';
	import { MessageSquare } from 'lucide-svelte';
	
	// Handle params prop to avoid warning
	export const data = {};
	
	let email = '';
	let password = '';
	let loading = false;
	let error = '';
	
	async function handleLogin() {
		if (!email || !password) {
			error = 'Please enter both email and password';
			return;
		}
		
		try {
			loading = true;
			error = '';
			
			const response = await fetch('/api/auth/login', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				credentials: 'include',
				body: JSON.stringify({ email, password })
			});
			
			if (response.ok) {
				const data = await response.json();
				if (data.success) {
					goto('/');
				} else {
					error = data.error || 'Login failed';
				}
			} else {
				const data = await response.json();
				error = data.error || 'Login failed';
			}
		} catch (err) {
			error = 'Network error';
			console.error('Login error:', err);
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Login - Internal Assistant</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full space-y-8">
		<div>
			<div class="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-primary-100">
				<MessageSquare class="h-6 w-6 text-primary-600" />
			</div>
			<h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
				Internal Assistant
			</h2>
			<p class="mt-2 text-center text-sm text-gray-600">
				Sign in to access your aggregated data
			</p>
		</div>
		
		<form class="mt-8 space-y-6" on:submit|preventDefault={handleLogin}>
			{#if error}
				<div class="bg-red-50 border border-red-200 rounded-md p-4">
					<p class="text-red-800 text-sm">{error}</p>
				</div>
			{/if}
			
			<div class="space-y-4">
				<div>
					<label for="email" class="block text-sm font-medium text-gray-700">
						Email address
					</label>
					<input
						id="email"
						name="email"
						type="email"
						required
						bind:value={email}
						class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
						placeholder="Enter your email"
					/>
				</div>
				
				<div>
					<label for="password" class="block text-sm font-medium text-gray-700">
						Password
					</label>
					<input
						id="password"
						name="password"
						type="password"
						required
						bind:value={password}
						class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
						placeholder="Enter your password"
					/>
				</div>
			</div>
			
			<div>
				<button
					type="submit"
					disabled={loading}
					class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{#if loading}
						<div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
					{/if}
					{loading ? 'Signing in...' : 'Sign in'}
				</button>
			</div>
		</form>
		
		<div class="text-center">
			<p class="text-xs text-gray-500">
				For MVP, use any email from the allowed users list
			</p>
		</div>
	</div>
</div>
