<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    
    let documents = [];
    let loading = false;
    let uploadLoading = false;
    let error = '';
    let success = '';
    let selectedFiles = [];
    let searchQuery = '';
    let searchResults = [];
    let searching = false;
    let uploadProgress = [];
    let duplicateFiles = [];
    let showDuplicateModal = false;
    let duplicateFileToReplace = null;
    let replaceLoading = false;
    
    // New variables for checkbox functionality
    let selectedDocuments = new Set();
    let selectAll = false;
    let deleteLoading = false;
    
    // Check authentication on mount
    onMount(async () => {
        const response = await fetch('/api/auth/check', {
            credentials: 'include'
        });
        
        if (!response.ok) {
            goto('/login');
            return;
        }
        
        loadDocuments();
    });
    
    // Function to handle select all checkbox
    function handleSelectAll(event) {
        selectAll = event.target.checked;
        if (selectAll) {
            // Select all documents
            selectedDocuments = new Set(documents.map(doc => doc.filename));
        } else {
            // Deselect all documents
            selectedDocuments = new Set();
        }
    }
    
    // Function to handle individual document selection
    function handleDocumentSelect(filename, checked) {
        if (checked) {
            selectedDocuments = new Set([...selectedDocuments, filename]);
        } else {
            selectedDocuments = new Set([...selectedDocuments].filter(doc => doc !== filename));
        }
        
        // Update select all state
        selectAll = selectedDocuments.size === documents.length;
    }
    
    // Function to delete selected documents
    async function deleteSelectedDocuments() {
        if (selectedDocuments.size === 0) {
            error = 'Please select documents to delete';
            return;
        }
        
        if (!confirm(`Are you sure you want to delete ${selectedDocuments.size} selected document(s)?`)) {
            return;
        }
        
        deleteLoading = true;
        error = '';
        
        try {
            // Delete documents sequentially to avoid race conditions
            const results = [];
            for (const filename of selectedDocuments) {
                const response = await fetch(`/api/documents/delete/${encodeURIComponent(filename)}`, {
                    method: 'DELETE',
                    credentials: 'include'
                });
                const result = await response.json();
                results.push(result);
            }
            
            const successful = results.filter(r => r.success !== false).length;
            const failed = results.length - successful;
            
            if (successful > 0) {
                success = `Successfully deleted ${successful} document(s)!`;
            }
            
            if (failed > 0) {
                error = `Failed to delete ${failed} document(s).`;
            }
            
            // Clear selections and reload documents
            selectedDocuments = new Set();
            selectAll = false;
            await loadDocuments();
        } catch (err) {
            error = 'Network error during bulk delete';
        } finally {
            deleteLoading = false;
        }
    }
    
    async function loadDocuments() {
        loading = true;
        error = '';
        
        try {
            const response = await fetch('/api/documents/list', {
                credentials: 'include'
            });
            
            if (response.ok) {
                const data = await response.json();
                documents = data.documents || [];
            } else {
                error = 'Failed to load documents';
            }
        } catch (err) {
            error = 'Network error while loading documents';
        } finally {
            loading = false;
        }
    }
    
    function handleFileSelect(event) {
        const files = Array.from(event.target.files);
        selectedFiles = [];
        error = '';
        
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
        const maxFileSize = 10 * 1024 * 1024; // 10MB
        
        for (const file of files) {
            // Check file type
            if (!allowedTypes.includes(file.type)) {
                error = `Invalid file type for "${file.name}". Please upload PDF or Word documents only.`;
                continue;
            }
            
            // Check file size
            if (file.size > maxFileSize) {
                error = `File "${file.name}" is too large. Please upload files smaller than 10MB.`;
                continue;
            }
            
            selectedFiles.push(file);
        }
        
        // Reset file input if there were errors
        if (error) {
            document.getElementById('file-input').value = '';
        }
    }
    
    async function uploadDocuments() {
        if (selectedFiles.length === 0) {
            error = 'Please select files to upload';
            return;
        }
        
        uploadLoading = true;
        error = '';
        success = '';
        uploadProgress = [];
        duplicateFiles = [];
        
        try {
            const formData = new FormData();
            
            // Add all files to form data
            selectedFiles.forEach(file => {
                formData.append('files', file);
            });
            
            const response = await fetch('/api/documents/upload', {
                method: 'POST',
                credentials: 'include',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Check for duplicates
                if (data.duplicates_found && data.duplicates_found.length > 0) {
                    duplicateFiles = data.duplicates_found;
                    showDuplicateModal = true;
                    return;
                }
                
                // Process results
                const successfulUploads = data.results.filter(r => r.success);
                const failedUploads = data.results.filter(r => !r.success);
                
                if (successfulUploads.length > 0) {
                    success = `Successfully uploaded ${successfulUploads.length} document(s)! ${data.total_chunks_added} chunks processed.`;
                }
                
                if (failedUploads.length > 0) {
                    error = `Failed to upload ${failedUploads.length} document(s). Check the details below.`;
                }
                
                // Set upload progress for display
                uploadProgress = data.results;
                
                selectedFiles = [];
                // Reset file input
                document.getElementById('file-input').value = '';
                // Reload documents list
                await loadDocuments();
            } else {
                error = data.error || 'Upload failed';
            }
        } catch (err) {
            error = 'Network error during upload';
        } finally {
            uploadLoading = false;
        }
    }
    
    async function handleDuplicateChoice(action, filename) {
        if (action === 'skip') {
            // Remove the duplicate file from the list
            duplicateFiles = duplicateFiles.filter(f => f !== filename);
            
            if (duplicateFiles.length === 0) {
                showDuplicateModal = false;
                // Continue with the upload
                await uploadDocuments();
            }
        } else if (action === 'replace') {
            replaceLoading = true;
            
            try {
                // Find the file in selectedFiles
                const fileToReplace = selectedFiles.find(f => f.name === filename);
                if (!fileToReplace) {
                    error = 'File not found for replacement';
                    return;
                }
                
                const formData = new FormData();
                formData.append('file', fileToReplace);
                
                const response = await fetch('/api/documents/replace', {
                    method: 'POST',
                    credentials: 'include',
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    success = `Document "${filename}" replaced successfully! ${data.chunks_added} chunks processed.`;
                    
                    // Remove the file from selectedFiles and duplicateFiles
                    selectedFiles = selectedFiles.filter(f => f.name !== filename);
                    duplicateFiles = duplicateFiles.filter(f => f !== filename);
                    
                    if (duplicateFiles.length === 0) {
                        showDuplicateModal = false;
                        // Continue with remaining files
                        if (selectedFiles.length > 0) {
                            await uploadDocuments();
                        } else {
                            // Reset file input and reload documents
                            document.getElementById('file-input').value = '';
                            await loadDocuments();
                        }
                    }
                } else {
                    error = data.error || 'Replace failed';
                }
            } catch (err) {
                error = 'Network error during replace';
            } finally {
                replaceLoading = false;
            }
        }
    }
    
    function closeDuplicateModal() {
        showDuplicateModal = false;
        duplicateFiles = [];
        selectedFiles = [];
        document.getElementById('file-input').value = '';
    }
    
    async function deleteDocument(filename) {
        if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
            return;
        }
        
        try {
            const response = await fetch(`/api/documents/delete/${encodeURIComponent(filename)}`, {
                method: 'DELETE',
                credentials: 'include'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                success = `Document "${filename}" deleted successfully!`;
                await loadDocuments();
            } else {
                error = data.error || 'Delete failed';
            }
        } catch (err) {
            error = 'Network error during delete';
        }
    }
    
    async function searchDocuments() {
        if (!searchQuery.trim()) {
            searchResults = [];
            return;
        }
        
        searching = true;
        
        try {
            const response = await fetch('/api/documents/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify({ query: searchQuery })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                searchResults = data.results || [];
            } else {
                error = data.error || 'Search failed';
                searchResults = [];
            }
        } catch (err) {
            error = 'Network error during search';
            searchResults = [];
        } finally {
            searching = false;
        }
    }
    

    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    function getFileIcon(fileType) {
        switch (fileType.toLowerCase()) {
            case 'pdf':
                return '📄';
            case 'docx':
            case 'doc':
                return '📝';
            default:
                return '📎';
        }
    }
</script>

<svelte:head>
    <title>Documents - Internal Assistant</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <!-- Header -->
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900">Documents</h1>
            <p class="mt-2 text-gray-600">Upload and manage documents for the AI assistant to reference</p>
        </div>
        
        <!-- Error/Success Messages -->
        {#if error}
            <div class="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-red-800">{error}</p>
                    </div>
                </div>
            </div>
        {/if}
        
        {#if success}
            <div class="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-green-800">{success}</p>
                    </div>
                </div>
            </div>
        {/if}
        
        <!-- Upload Section -->
        <div class="bg-white shadow rounded-lg p-6 mb-8">
            <h2 class="text-lg font-medium text-gray-900 mb-4">Upload Documents</h2>
            
            <div class="space-y-4">
                <div>
                    <label for="file-input" class="block text-sm font-medium text-gray-700 mb-2">
                        Select Files
                    </label>
                    <input
                        id="file-input"
                        type="file"
                        accept=".pdf,.docx,.doc"
                        multiple
                        on:change={handleFileSelect}
                        class="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                    />
                    <p class="mt-1 text-sm text-gray-500">
                        Supported formats: PDF, DOCX, DOC (Max 10MB per file)
                    </p>
                </div>
                
                {#if selectedFiles.length > 0}
                    <div class="p-3 bg-blue-50 rounded-md">
                        <p class="text-sm font-medium text-blue-800 mb-2">Selected Files ({selectedFiles.length}):</p>
                        <div class="max-h-32 overflow-y-auto">
                            <ul class="text-sm text-blue-700 space-y-1">
                                {#each selectedFiles as file}
                                    <li class="flex items-center justify-between">
                                        <span class="truncate">{file.name}</span>
                                        <span class="text-xs text-blue-600 flex-shrink-0 ml-2">({formatFileSize(file.size)})</span>
                                    </li>
                                {/each}
                            </ul>
                        </div>
                    </div>
                {/if}
                
                <button
                    on:click={uploadDocuments}
                    disabled={selectedFiles.length === 0 || uploadLoading}
                    class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {#if uploadLoading}
                        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Processing {selectedFiles.length} file(s)...
                    {:else}
                        Upload {selectedFiles.length > 0 ? selectedFiles.length : ''} Document{selectedFiles.length !== 1 ? 's' : ''}
                    {/if}
                </button>
            </div>
            
            <!-- Upload Progress -->
            {#if uploadProgress.length > 0}
                <div class="mt-6">
                    <h3 class="text-md font-medium text-gray-900 mb-3">Upload Results</h3>
                    <div class="space-y-3 max-h-64 overflow-y-auto">
                        {#each uploadProgress as result}
                            <div class="p-4 border rounded-md {result.success ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}">
                                <div class="flex items-start justify-between">
                                    <div class="flex-1">
                                        <div class="flex items-center">
                                            {#if result.success}
                                                <svg class="h-5 w-5 text-green-400 mr-2" viewBox="0 0 20 20" fill="currentColor">
                                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                                                </svg>
                                            {:else}
                                                <svg class="h-5 w-5 text-red-400 mr-2" viewBox="0 0 20 20" fill="currentColor">
                                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                                                </svg>
                                            {/if}
                                            <span class="font-medium {result.success ? 'text-green-800' : 'text-red-800'}">{result.filename}</span>
                                        </div>
                                        {#if result.success}
                                            <p class="text-sm text-green-700 mt-1">
                                                {result.chunks_added} chunks processed • {formatFileSize(result.file_size)}
                                            </p>
                                        {:else}
                                            <p class="text-sm text-red-700 mt-1">{result.error}</p>
                                        {/if}
                                    </div>
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>
            {/if}
        </div>
        
        <!-- Search Section -->
        <div class="bg-white shadow rounded-lg p-6 mb-8">
            <h2 class="text-lg font-medium text-gray-900 mb-4">Search Documents</h2>
            
            <div class="flex space-x-4">
                <div class="flex-1">
                    <input
                        type="text"
                        bind:value={searchQuery}
                        placeholder="Search within uploaded documents..."
                        class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                </div>
                <button
                    on:click={searchDocuments}
                    disabled={!searchQuery.trim() || searching}
                    class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {#if searching}
                        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Searching...
                    {:else}
                        Search
                    {/if}
                </button>
            </div>
            
            {#if searchResults.length > 0}
                <div class="mt-6">
                    <h3 class="text-md font-medium text-gray-900 mb-3">Search Results ({searchResults.length})</h3>
                    <div class="space-y-3 max-h-64 overflow-y-auto">
                        {#each searchResults as result}
                            <div class="p-4 border border-gray-200 rounded-md">
                                <div class="flex items-start justify-between">
                                    <div class="flex-1">
                                        <p class="text-sm font-medium text-gray-900">{result.source}</p>
                                        <p class="text-sm text-gray-600 mt-1">{result.content}</p>
                                    </div>
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>
            {/if}
        </div>
        
        <!-- Documents List -->
        <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
                <h2 class="text-lg font-medium text-gray-900">Uploaded Documents ({documents.length})</h2>
            </div>
            
            {#if loading}
                <div class="p-6 text-center">
                    <svg class="animate-spin h-8 w-8 text-blue-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <p class="mt-2 text-gray-600">Loading documents...</p>
                </div>
            {:else if documents.length === 0}
                <div class="p-6 text-center">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h3 class="mt-2 text-sm font-medium text-gray-900">No documents</h3>
                    <p class="mt-1 text-sm text-gray-500">Get started by uploading a document above.</p>
                </div>
            {:else}
                <div class="divide-y divide-gray-200">
                    <!-- Selection Header -->
                    <div class="px-6 py-4 flex items-center justify-between bg-gray-50">
                        <div class="flex items-center">
                            <input
                                id="select-all-checkbox"
                                type="checkbox"
                                checked={selectAll}
                                on:change={handleSelectAll}
                                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                            <label for="select-all-checkbox" class="ml-2 text-sm font-medium text-gray-700">Select All</label>
                        </div>
                        {#if selectedDocuments.size > 0}
                            <button
                                on:click={deleteSelectedDocuments}
                                disabled={deleteLoading}
                                class="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
                            >
                                {#if deleteLoading}
                                    <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-red-700" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Deleting...
                                {:else}
                                    Delete Selected ({selectedDocuments.size})
                                {/if}
                            </button>
                        {/if}
                    </div>
                    
                    {#each documents as document}
                        <div class="px-6 py-4 hover:bg-gray-50">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center space-x-3">
                                    <input
                                        type="checkbox"
                                        checked={selectedDocuments.has(document.filename)}
                                        on:change={(event) => handleDocumentSelect(document.filename, event.target.checked)}
                                        class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                    />
                                    <span class="text-2xl">{getFileIcon(document.file_type)}</span>
                                    <div>
                                        <h3 class="text-sm font-medium text-gray-900">{document.filename}</h3>
                                        <p class="text-sm text-gray-500">
                                            {document.file_type.toUpperCase()} • {document.chunks} chunks
                                        </p>
                                    </div>
                                </div>
                                <button
                                    on:click={() => deleteDocument(document.filename)}
                                    class="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>
    </div>
</div>

<!-- Duplicate Files Modal -->
{#if showDuplicateModal}
    <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
        <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div class="mt-3">
                <div class="flex items-center justify-center w-12 h-12 mx-auto bg-yellow-100 rounded-full">
                    <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                    </svg>
                </div>
                <div class="mt-4 text-center">
                    <h3 class="text-lg font-medium text-gray-900">Duplicate Files Found</h3>
                    <div class="mt-2 px-7 py-3">
                        <p class="text-sm text-gray-500 mb-4">
                            The following files already exist. Choose what to do with each file:
                        </p>
                        <div class="space-y-3 max-h-64 overflow-y-auto">
                            {#each duplicateFiles as filename}
                                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                                    <span class="text-sm font-medium text-gray-900 truncate">{filename}</span>
                                    <div class="flex space-x-2 ml-2">
                                        <button
                                            on:click={() => handleDuplicateChoice('skip', filename)}
                                            disabled={replaceLoading}
                                            class="px-3 py-1 text-xs font-medium text-gray-600 bg-gray-200 rounded-md hover:bg-gray-300 disabled:opacity-50"
                                        >
                                            Skip
                                        </button>
                                        <button
                                            on:click={() => handleDuplicateChoice('replace', filename)}
                                            disabled={replaceLoading}
                                            class="px-3 py-1 text-xs font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
                                        >
                                            {replaceLoading ? 'Replacing...' : 'Replace'}
                                        </button>
                                    </div>
                                </div>
                            {/each}
                        </div>
                    </div>
                </div>
                <div class="flex justify-center mt-4">
                    <button
                        on:click={closeDuplicateModal}
                        class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
                    >
                        Cancel All
                    </button>
                </div>
            </div>
        </div>
    </div>
{/if}
