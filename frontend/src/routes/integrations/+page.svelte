<script>
	import { onMount } from 'svelte';
	import { MessageSquare, GitBranch, Mail, RefreshCw, CheckCircle, XCircle } from 'lucide-svelte';
	
	// Handle params prop to avoid warning
	export const data = {};
	
	// Integration state
	let integrations = {
		slack: { connected: false, status: 'disconnected' },
		github: { connected: false, status: 'disconnected' },
		outlook: { connected: false, status: 'disconnected' }
	};
	
	let loading = true;
	let syncing = false;
	let error = null;
	
	onMount(async () => {
		await loadIntegrations();
	});
	
	async function loadIntegrations() {
		try {
			loading = true;
			const response = await fetch('/api/integrations', {
				credentials: 'include'
			});
			
			if (response.ok) {
				integrations = await response.json();
			} else {
				error = 'Failed to load integrations';
			}
		} catch (err) {
			error = 'Network error';
			console.error('Load integrations error:', err);
		} finally {
			loading = false;
		}
	}
	
	async function syncAll() {
		try {
			syncing = true;
			const response = await fetch('/api/integrations/sync/all', {
				method: 'POST',
				credentials: 'include'
			});
			
			if (response.ok) {
				await loadIntegrations(); // Reload data
			}
		} catch (err) {
			console.error('Sync all error:', err);
		} finally {
			syncing = false;
		}
	}
	
	async function syncIntegration(type) {
		try {
			syncing = true;
			const response = await fetch(`/api/integrations/${type}/sync`, {
				method: 'POST',
				credentials: 'include'
			});
			
			if (response.ok) {
				await loadIntegrations(); // Reload data
			}
		} catch (err) {
			console.error(`Sync ${type} error:`, err);
		} finally {
			syncing = false;
		}
	}
	
	async function connectIntegration(type) {
		try {
			const response = await fetch(`/api/integrations/connect`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				credentials: 'include',
				body: JSON.stringify({ type })
			});
			
			if (response.ok) {
				await loadIntegrations(); // Reload data
			}
		} catch (err) {
			console.error('Connect integration error:', err);
		}
	}
	
	async function disconnectIntegration(type) {
		try {
			const response = await fetch(`/api/integrations/disconnect`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				credentials: 'include',
				body: JSON.stringify({ type })
			});
			
			if (response.ok) {
				await loadIntegrations(); // Reload data
			}
		} catch (err) {
			console.error('Disconnect integration error:', err);
		}
	}
	
	function formatLastSync(lastSync) {
		if (!lastSync) return 'Never';
		return new Date(lastSync).toLocaleString();
	}
</script>

<svelte:head>
	<title>Integrations - Internal Assistant</title>
</svelte:head>

<div class="p-6">
	<!-- Header -->
	<div class="mb-8">
		<h1 class="text-2xl font-bold text-gray-900">Integrations</h1>
		<p class="text-gray-600 mt-2">Manage your data source connections</p>
	</div>
	
	{#if loading}
		<div class="flex items-center justify-center h-64">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
		</div>
	{:else}
		<!-- Sync All Button -->
		<div class="mb-6">
			<button 
				on:click={syncAll}
				disabled={syncing}
				class="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
			>
				{#if syncing}
					<RefreshCw class="w-4 h-4 mr-2 animate-spin" />
				{:else}
					<RefreshCw class="w-4 h-4 mr-2" />
				{/if}
				{syncing ? 'Syncing...' : 'Sync All'}
			</button>
		</div>
		
		<!-- Integration Cards -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
			<!-- Slack Integration -->
			<div class="bg-white rounded-lg shadow p-6">
				<div class="flex items-center justify-between mb-4">
					<div class="flex items-center">
						<div class="p-2 bg-blue-100 rounded-lg">
							<MessageSquare class="w-6 h-6 text-blue-600" />
						</div>
						<div class="ml-3">
							<h3 class="text-lg font-semibold text-gray-900">Slack</h3>
							<div class="flex items-center mt-1">
								{#if integrations.slack.connected}
									<CheckCircle class="w-4 h-4 text-green-600 mr-1" />
									<span class="text-sm text-green-600">Connected</span>
								{:else}
									<XCircle class="w-4 h-4 text-red-600 mr-1" />
									<span class="text-sm text-red-600">Not Connected</span>
								{/if}
							</div>
						</div>
					</div>
				</div>
				
				<div class="space-y-3">
					<div class="text-sm text-gray-600">
						<p><strong>Last Sync:</strong> {formatLastSync(integrations.slack.last_sync)}</p>
					</div>
					
					<button
						on:click={() => syncIntegration('slack')}
						disabled={syncing || !integrations.slack.connected}
						class="w-full px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						Sync Slack
					</button>
				</div>
			</div>
			
			<!-- GitHub Integration -->
			<div class="bg-white rounded-lg shadow p-6">
				<div class="flex items-center justify-between mb-4">
					<div class="flex items-center">
						<div class="p-2 bg-green-100 rounded-lg">
							<GitBranch class="w-6 h-6 text-green-600" />
						</div>
						<div class="ml-3">
							<h3 class="text-lg font-semibold text-gray-900">GitHub</h3>
							<div class="flex items-center mt-1">
								{#if integrations.github.connected}
									<CheckCircle class="w-4 h-4 text-green-600 mr-1" />
									<span class="text-sm text-green-600">Connected</span>
								{:else}
									<XCircle class="w-4 h-4 text-red-600 mr-1" />
									<span class="text-sm text-red-600">Not Connected</span>
								{/if}
							</div>
						</div>
					</div>
				</div>
				
				<div class="space-y-3">
					<div class="text-sm text-gray-600">
						<p><strong>Last Sync:</strong> {formatLastSync(integrations.github.last_sync)}</p>
					</div>
					
					<button
						on:click={() => syncIntegration('github')}
						disabled={syncing || !integrations.github.connected}
						class="w-full px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						Sync GitHub
					</button>
				</div>
			</div>
			
			<!-- Outlook Integration -->
			<div class="bg-white rounded-lg shadow p-6">
				<div class="flex items-center justify-between mb-4">
					<div class="flex items-center">
						<div class="p-2 bg-purple-100 rounded-lg">
							<Mail class="w-6 h-6 text-purple-600" />
						</div>
						<div class="ml-3">
							<h3 class="text-lg font-semibold text-gray-900">Outlook</h3>
							<div class="flex items-center mt-1">
								{#if integrations.outlook.connected}
									<CheckCircle class="w-4 h-4 text-green-600 mr-1" />
									<span class="text-sm text-green-600">Connected</span>
								{:else}
									<XCircle class="w-4 h-4 text-red-600 mr-1" />
									<span class="text-sm text-red-600">Not Connected</span>
								{/if}
							</div>
						</div>
					</div>
				</div>
				
				<div class="space-y-3">
					<div class="text-sm text-gray-600">
						<p><strong>Last Sync:</strong> {formatLastSync(integrations.outlook.last_sync)}</p>
					</div>
					
					<button
						on:click={() => syncIntegration('outlook')}
						disabled={syncing || !integrations.outlook.connected}
						class="w-full px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						Sync Outlook
					</button>
				</div>
			</div>
		</div>
		
		<!-- Configuration Info -->
		<div class="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
			<h3 class="text-lg font-semibold text-blue-900 mb-3">Configuration</h3>
			<p class="text-blue-800 text-sm mb-4">
				To connect these integrations, you'll need to configure the following environment variables:
			</p>
			
			<div class="space-y-2 text-sm">
				<div class="bg-white p-3 rounded border">
					<strong class="text-blue-900">Slack:</strong> SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_SIGNING_SECRET
				</div>
				<div class="bg-white p-3 rounded border">
					<strong class="text-blue-900">GitHub:</strong> GITHUB_ACCESS_TOKEN, GITHUB_ORG_NAME
				</div>
				<div class="bg-white p-3 rounded border">
					<strong class="text-blue-900">Outlook:</strong> MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET, MICROSOFT_TENANT_ID
				</div>
			</div>
		</div>
	{/if}
</div>
