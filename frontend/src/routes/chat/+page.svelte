<script>
	import { onMount } from 'svelte';
	import { Send, Bot, User } from 'lucide-svelte';
	
	// Handle params prop to avoid warning
	export const data = {};
	
	let message = '';
	let messages = [];
	let loading = false;
	let chatContainer;
	
	onMount(() => {
		scrollToBottom();
	});
	
	function scrollToBottom() {
		if (chatContainer) {
			chatContainer.scrollTop = chatContainer.scrollHeight;
		}
	}
	
	async function sendMessage() {
		if (!message.trim() || loading) return;
		
		const userMessage = {
			id: Date.now(),
			text: message,
			sender: 'user',
			timestamp: new Date().toISOString()
		};
		
		messages = [...messages, userMessage];
		const currentMessage = message;
		message = '';
		loading = true;
		
		// Scroll to bottom after adding user message
		setTimeout(scrollToBottom, 100);
		
		try {
			const response = await fetch('/api/chat/send', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				credentials: 'include',
				body: JSON.stringify({ message: currentMessage })
			});
			
			if (response.ok) {
				const data = await response.json();
				const botMessage = {
					id: Date.now() + 1,
					text: data.response,
					sender: 'bot',
					timestamp: new Date().toISOString(),
					sources: data.sources || []
				};
				
				messages = [...messages, botMessage];
			} else {
				const errorMessage = {
					id: Date.now() + 1,
					text: 'Sorry, I encountered an error. Please try again.',
					sender: 'bot',
					timestamp: new Date().toISOString()
				};
				
				messages = [...messages, errorMessage];
			}
		} catch (err) {
			console.error('Chat error:', err);
			const errorMessage = {
				id: Date.now() + 1,
				text: 'Sorry, I encountered a network error. Please try again.',
				sender: 'bot',
				timestamp: new Date().toISOString()
			};
			
			messages = [...messages, errorMessage];
		} finally {
			loading = false;
			setTimeout(scrollToBottom, 100);
		}
	}
	
	function handleKeyPress(event) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			sendMessage();
		}
	}
</script>

<svelte:head>
	<title>Chat - Internal Assistant</title>
</svelte:head>

<div class="flex flex-col h-full">
	<!-- Header -->
	<div class="bg-white border-b border-gray-200 px-6 py-4">
		<h1 class="text-xl font-semibold text-gray-900">Chat with AI Assistant</h1>
		<p class="text-sm text-gray-600 mt-1">Ask questions about your aggregated data</p>
	</div>
	
	<!-- Chat Messages -->
	<div 
		bind:this={chatContainer}
		class="flex-1 overflow-y-auto p-6 space-y-4"
	>
		{#if messages.length === 0}
			<div class="text-center py-12">
				<Bot class="w-12 h-12 text-gray-400 mx-auto mb-4" />
				<h3 class="text-lg font-medium text-gray-900 mb-2">Welcome to Internal Assistant</h3>
				<p class="text-gray-600 max-w-md mx-auto">
					I can help you find information from your Slack, GitHub, and Outlook data. 
					Try asking me something like "What's the latest activity in our development team?" 
					or "Show me recent emails from the marketing team."
				</p>
			</div>
		{/if}
		
		{#each messages as msg}
			<div class="flex {msg.sender === 'user' ? 'justify-end' : 'justify-start'}">
				<div class="max-w-3xl {msg.sender === 'user' ? 'bg-primary-600 text-white' : 'bg-white border border-gray-200'} rounded-lg px-4 py-3 shadow-sm">
					<div class="flex items-start space-x-3">
						{#if msg.sender === 'user'}
							<User class="w-5 h-5 mt-1 flex-shrink-0" />
						{:else}
							<Bot class="w-5 h-5 mt-1 flex-shrink-0 text-gray-600" />
						{/if}
						
						<div class="flex-1">
							<p class="text-sm whitespace-pre-wrap">{msg.text}</p>
							
							{#if msg.sources && msg.sources.length > 0}
								<div class="mt-3 pt-3 border-t {msg.sender === 'user' ? 'border-primary-200' : 'border-gray-200'}">
									<p class="text-xs {msg.sender === 'user' ? 'text-primary-200' : 'text-gray-500'} mb-2">Sources:</p>
									<div class="space-y-1">
										{#each msg.sources as source}
											<div class="text-xs {msg.sender === 'user' ? 'text-primary-200' : 'text-gray-600'}">
												• {source.source}: {source.content.substring(0, 100)}...
											</div>
										{/each}
									</div>
								</div>
							{/if}
							
							<p class="text-xs {msg.sender === 'user' ? 'text-primary-200' : 'text-gray-400'} mt-2">
								{new Date(msg.timestamp).toLocaleTimeString()}
							</p>
						</div>
					</div>
				</div>
			</div>
		{/each}
		
		{#if loading}
			<div class="flex justify-start">
				<div class="bg-white border border-gray-200 rounded-lg px-4 py-3 shadow-sm">
					<div class="flex items-center space-x-3">
						<Bot class="w-5 h-5 text-gray-600" />
						<div class="flex space-x-1">
							<div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
							<div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
							<div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
	
	<!-- Message Input -->
	<div class="bg-white border-t border-gray-200 px-6 py-4">
		<div class="flex space-x-4">
			<div class="flex-1">
				<textarea
					bind:value={message}
					on:keypress={handleKeyPress}
					placeholder="Ask me about your data..."
					class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
					rows="1"
					disabled={loading}
				></textarea>
			</div>
			<button
				on:click={sendMessage}
				disabled={!message.trim() || loading}
				class="px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
			>
				<Send class="w-5 h-5" />
			</button>
		</div>
	</div>
</div>
