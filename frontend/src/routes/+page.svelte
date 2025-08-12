<script>
	import { onMount } from 'svelte';
	import { MessageSquare, GitBranch, Mail, Activity } from 'lucide-svelte';
	
	// Handle params prop to avoid warning
	export const data = {};
	
	// Data state
	let summary = {
		slack: { count: 0, channels: 0, mentions: 0 },
		github: { count: 0, repos: 0, commits: 0, prs: 0, issues: 0 },
		outlook: { count: 0, unread: 0, folders: 0 },
		total_items: 0
	};
	
	let loading = true;
	let error = null;
	
	onMount(async () => {
		await loadSummary();
	});
	
	async function loadSummary() {
		try {
			loading = true;
			const response = await fetch('/api/data/summary', {
				credentials: 'include'
			});
			
			if (response.ok) {
				summary = await response.json();
			} else if (response.status === 401) {
				// User not authenticated, this will be handled by layout
				error = 'Authentication required';
			} else {
				error = 'Failed to load summary';
			}
		} catch (err) {
			error = 'Network error';
			console.error('Load summary error:', err);
		} finally {
			loading = false;
		}
	}
	
	async function syncAll() {
		try {
			const response = await fetch('/api/integrations/sync/all', {
				method: 'POST',
				credentials: 'include'
			});
			
			if (response.ok) {
				await loadSummary(); // Reload data
			}
		} catch (err) {
			console.error('Sync error:', err);
		}
	}
</script>

<svelte:head>
	<title>Dashboard - Internal Assistant</title>
</svelte:head>

<div class="p-6">
	<!-- Header -->
	<div class="mb-8">
		<h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
		<p class="text-gray-600 mt-2">Overview of your aggregated data</p>
	</div>
	
	{#if loading}
		<div class="flex items-center justify-center h-64">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
		</div>
	{:else if error}
		<div class="bg-red-50 border border-red-200 rounded-md p-4">
			<p class="text-red-800">{error}</p>
		</div>
	{:else}
		<!-- Sync Button -->
		<div class="mb-6">
			<button 
				on:click={syncAll}
				class="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors"
			>
				Sync All Data
			</button>
		</div>
		
		<!-- Summary Cards -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
			<!-- Slack Card -->
			<div class="bg-white rounded-lg shadow p-6">
				<div class="flex items-center">
					<div class="p-2 bg-blue-100 rounded-lg">
						<MessageSquare class="w-6 h-6 text-blue-600" />
					</div>
					<div class="ml-4">
						<h3 class="text-lg font-semibold text-gray-900">Slack</h3>
						<p class="text-2xl font-bold text-blue-600">{summary.slack.count}</p>
					</div>
				</div>
				<div class="mt-4 text-sm text-gray-600">
					<p>{summary.slack.channels} channels • {summary.slack.mentions} mentions</p>
				</div>
			</div>
			
			<!-- GitHub Card -->
			<div class="bg-white rounded-lg shadow p-6">
				<div class="flex items-center">
					<div class="p-2 bg-green-100 rounded-lg">
						<GitBranch class="w-6 h-6 text-green-600" />
					</div>
					<div class="ml-4">
						<h3 class="text-lg font-semibold text-gray-900">GitHub</h3>
						<p class="text-2xl font-bold text-green-600">{summary.github.count}</p>
					</div>
				</div>
				<div class="mt-4 text-sm text-gray-600">
					<p>{summary.github.repos} repos • {summary.github.commits} commits • {summary.github.prs} PRs</p>
				</div>
			</div>
			
			<!-- Outlook Card -->
			<div class="bg-white rounded-lg shadow p-6">
				<div class="flex items-center">
					<div class="p-2 bg-purple-100 rounded-lg">
						<Mail class="w-6 h-6 text-purple-600" />
					</div>
					<div class="ml-4">
						<h3 class="text-lg font-semibold text-gray-900">Outlook</h3>
						<p class="text-2xl font-bold text-purple-600">{summary.outlook.count}</p>
					</div>
				</div>
				<div class="mt-4 text-sm text-gray-600">
					<p>{summary.outlook.unread} unread • {summary.outlook.folders} folders</p>
				</div>
			</div>
		</div>
		
		<!-- Quick Actions -->
		<div class="bg-white rounded-lg shadow p-6">
			<h2 class="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
				<a href="/chat" class="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
					<MessageSquare class="w-5 h-5 text-gray-600 mr-3" />
					<span class="text-sm font-medium text-gray-900">Chat with AI</span>
				</a>
				
				<a href="/integrations" class="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
					<Activity class="w-5 h-5 text-gray-600 mr-3" />
					<span class="text-sm font-medium text-gray-900">Manage Integrations</span>
				</a>
				
				<button class="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
					<GitBranch class="w-5 h-5 text-gray-600 mr-3" />
					<span class="text-sm font-medium text-gray-900">View GitHub Activity</span>
				</button>
				
				<button class="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
					<Mail class="w-5 h-5 text-gray-600 mr-3" />
					<span class="text-sm font-medium text-gray-900">Check Emails</span>
				</button>
			</div>
		</div>
	{/if}
</div>
