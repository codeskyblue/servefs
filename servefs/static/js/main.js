const { createApp, ref, computed, onMounted, onUnmounted, watch, nextTick } = Vue;
const { ElMessage, ElMessageBox } = ElementPlus;

const app = createApp({
    setup() {
        const currentPath = ref('');
        const fileList = ref([]);
        const isDragOver = ref(false);
        const uploadProgress = ref([]);
        const fileInput = ref(null);
        const folderInput = ref(null);
        const previewDialog = ref({
            visible: false,
            title: '',
            content: '',
            editable: false,
            currentFile: null,
            isImage: false,
            isVideo: false,
            isText: false,
            isFont: false,
            fontUrl: '',
            fontFamily: '',
            fileSize: 0,
            mimeType: '',
            currentImageIndex: -1
        });
        const deleteDialog = ref({
            visible: false,
            title: '',
            message: ''
        });
        const previewText = ref('Hello 你好 こんにちは 123');
        const hasWritePermission = ref(false);  // 添加权限状态

        // Get initial path from URL
        const initPath = () => {
            const path = window.location.pathname;
            if (path.startsWith('/blob/')) {
                return path.substring(6); // Remove '/blob/' prefix
            }
            return '';
        };

        const pathSegments = computed(() => {
            return currentPath.value ? currentPath.value.split('/') : [];
        });

        const getPathUpTo = (index) => {
            return pathSegments.value.slice(0, index + 1).join('/');
        };

        const navigateTo = (path) => {
            const urlPath = path ? `/blob/${path}` : '/';
            history.pushState(null, '', urlPath);
            loadFiles(path);
        };

        const loadFiles = async (path = '') => {
            try {
                const response = await fetch(`/api/files?path=${encodeURIComponent(path)}`);
                const data = await response.json();
                if (data.error) {
                    ElMessage.error(data.error);
                    return;
                }
                // 为每个文件项添加 tooltip 相关属性
                fileList.value = data.items.map(item => ({
                    ...item,
                    tooltipText: 'Copy Link',
                    showTooltip: false
                }));
                currentPath.value = data.current_path;
            } catch (error) {
                ElMessage.error('Failed to load files');
            }
        };

        const handleItemClick = (item) => {
            if (item.type === 'directory') {
                navigateTo(item.path);
            } else {
                openFile(item);
            }
        };

        // 检查文件是否为图片
        const isImageFile = (filename) => {
            const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'];
            return imageExtensions.some(ext => filename.toLowerCase().endsWith(ext));
        };

        // 检查文件是否为视频
        const isVideoFile = (filename) => {
            const videoExtensions = ['.mp4', '.webm', '.ogg', '.mov', '.mkv', '.avi'];
            return videoExtensions.some(ext => filename.toLowerCase().endsWith(ext));
        };

        const formatFileSize = (bytes) => {
            if (bytes === 0) return '0 B';
            const k = 1024;
            const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        };

        const createPreviewConfig = (item, type) => {
            return {
                visible: true,
                title: item.name,
                content: (type === 'image' || type === 'video') ? `/raw/${item.path}` : '',
                editable: type === 'text',
                currentFile: item,
                isImage: type === 'image',
                isVideo: type === 'video',
                isText: type === 'text',
                isFont: type === 'font',
                fontUrl: type === 'font' ? `/raw/${item.path}` : '',
                fontFamily: '',
                fileSize: item.size || 0,
                mimeType: item.mime_type || ''
            };
        };

        const openFile = async (item) => {
            try {
                if (isImageFile(item.name)) {
                    previewDialog.value = createPreviewConfig(item, 'image');
                } else if (isVideoFile(item.name)) {
                    previewDialog.value = createPreviewConfig(item, 'video');
                } else if (item.name.toLowerCase().endsWith('.ttf')) {
                    previewDialog.value = createPreviewConfig(item, 'font');
                } else if (item.mime_type.startsWith('text/') || item.mime_type === 'application/json') {
                    const response = await fetch(`/api/files/${encodeURIComponent(item.path)}`);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    const data = await response.json();
                    if (data.error) {
                        ElMessage.error(data.error);
                        return;
                    }
                    const config = createPreviewConfig(item, 'text');
                    config.content = data.content;
                    previewDialog.value = config;
                } else {
                    previewDialog.value = createPreviewConfig(item, 'unknown');
                }
            } catch (error) {
                console.error('Error opening file:', error);
                ElMessage.error('打开文件时发生错误');
            }
        };

        const saveFile = async () => {
            try {
                const response = await fetch(`/api/files/${previewDialog.value.currentFile.path}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        content: previewDialog.value.content
                    })
                });
                const data = await response.json();
                if (data.error) {
                    ElMessage.error(data.error);
                    return;
                }
                ElMessage.success('File saved successfully');
            } catch (error) {
                ElMessage.error('Failed to save file');
            }
        };

        const saveAndClose = async () => {
            await saveFile();
            previewDialog.value.visible = false;
        };

        const showDeleteDialog = (item) => {
            deleteDialog.value = {
                visible: true,
                title: `Delete ${item.name}?`,
                message: `Are you sure you want to delete ${item.name}?`
            };
            deleteDialog.value.currentFile = item;
        };

        const confirmDelete = async () => {
            try {
                const response = await fetch(`/api/files/${deleteDialog.value.currentFile.path}`, {
                    method: 'DELETE'
                });
                const data = await response.json();
                if (data.error) {
                    ElMessage.error(data.error);
                    return;
                }
                ElMessage.success('Item deleted successfully');
                await loadFiles(currentPath.value);
                deleteDialog.value.visible = false;
            } catch (error) {
                ElMessage.error('Failed to delete item');
            }
        };

        const downloadFile = (item) => {
            const a = document.createElement('a');
            a.href = item.download_url;
            a.download = item.name;
            a.click();
        };

        // 复制文件链接的方法
        const copyFileLink = async (item) => {
            try {
                const fullUrl = new URL(item.download_url, window.location.origin).href;
                await navigator.clipboard.writeText(fullUrl);
                // 更新 tooltip 文本
                item.tooltipText = 'Copied';
            } catch (error) {
                item.tooltipText = 'Failed to copy';
            }
        };

        // 处理 tooltip 隐藏事件
        const onTooltipHide = (item) => {
            if (item.tooltipText !== 'Copy Link') {
                item.tooltipText = 'Copy Link';
            }
        };

        // 处理文件上传
        const uploadFiles = async (files) => {
            const formData = new FormData();
            const totalFiles = files.length;
            let processedFiles = 0;

            // 创建一个 Map 来存储文件夹结构
            const folderStructure = new Map();

            // 处理所有文件，构建文件夹结构
            for (const file of files) {
                const relativePath = file.webkitRelativePath || file.name;
                const pathParts = relativePath.split('/');
                
                // 如果是文件夹中的文件
                if (pathParts.length > 1) {
                    const folderPath = pathParts.slice(0, -1).join('/');
                    // 记录文件夹路径
                    folderStructure.set(folderPath, true);
                }

                formData.append('files', file);
                // 添加文件的相对路径信息
                formData.append('paths', relativePath);
                
                // 添加上传进度条
                uploadProgress.value.push({
                    filename: relativePath,
                    percentage: 0,
                    status: ''  // 默认状态为空
                });
            }

            try {
                const response = await fetch(`/api/upload/${currentPath.value}`, {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                if (data.error) {
                    ElMessage.error(data.error);
                    uploadProgress.value.forEach(p => p.status = 'error');
                    return;
                }
                ElMessage.success('文件上传成功');
                // 更新进度条
                uploadProgress.value.forEach(p => {
                    p.percentage = 100;
                    p.status = 'success';
                });
                // 清理进度条
                setTimeout(() => {
                    uploadProgress.value = [];
                }, 2000);
                // 刷新文件列表
                await loadFiles(currentPath.value);
            } catch (error) {
                ElMessage.error('文件上传失败');
                uploadProgress.value.forEach(p => p.status = 'error');
            }
        };

        const handleFileSelect = (event) => {
            const files = event.target.files;
            if (files.length > 0) {
                uploadFiles(files);
                event.target.value = ''; // 清理选择，允许重复选择相同文件
            }
        };

        const handleFileDrop = async (event) => {
            isDragOver.value = false;
            const items = event.dataTransfer.items;
            const files = [];

            // 递归获取文件夹中的所有文件
            const getFiles = async (entry) => {
                if (entry.isFile) {
                    const file = await new Promise((resolve) => entry.file(resolve));
                    // 保存完整路径信息
                    file.webkitRelativePath = entry.fullPath.substring(1); // 移除开头的 '/'
                    files.push(file);
                } else if (entry.isDirectory) {
                    const reader = entry.createReader();
                    const entries = await new Promise((resolve) => {
                        reader.readEntries(resolve);
                    });
                    for (const childEntry of entries) {
                        await getFiles(childEntry);
                    }
                }
            };

            // 处理所有拖放的项目
            for (const item of items) {
                if (item.kind === 'file') {
                    const entry = item.webkitGetAsEntry();
                    if (entry) {
                        await getFiles(entry);
                    }
                }
            }

            if (files.length > 0) {
                uploadFiles(files);
            }
        };

        // 添加键盘快捷键支持
        const handleKeydown = (e) => {
            if (previewDialog.value.visible && (e.metaKey || e.ctrlKey) && e.key === 's') {
                e.preventDefault(); // 阻止浏览器默认的保存行为
                saveFile();
            }
        };

        // Handle browser back/forward buttons
        window.addEventListener('popstate', () => {
            loadFiles(initPath());
        });

        // 检查用户权限
        const checkPermission = async () => {
            try {
                const response = await fetch('/api/auth/check');
                const data = await response.json();
                hasWritePermission.value = data.permission === 'read_write';
            } catch (error) {
                console.error('Failed to check permissions:', error);
                hasWritePermission.value = false;
            }
        };

        // 登录方法
        const login = async () => {
            try {
                const response = await fetch('/api/auth/login');
                if (response.ok) {
                    await checkPermission();
                    ElMessage.success('Login successful');
                }
            } catch (error) {
                console.error('Login failed:', error);
            }
        };

        // Load initial files based on URL path
        onMounted(() => {
            loadFiles(initPath());
            checkPermission();  // 检查权限
            window.addEventListener('keydown', handleKeydown);
        });

        onUnmounted(() => {
            window.removeEventListener('keydown', handleKeydown);
        });

        watch(() => previewDialog.value.fontUrl, (newUrl) => {
            if (newUrl && previewDialog.value.isFont) {
                const fontFamily = 'PreviewFont_' + Date.now();
                const style = document.createElement('style');
                style.textContent = `
                    @font-face {
                        font-family: '${fontFamily}';
                        src: url('${newUrl}') format('truetype');
                    }
                `;
                document.head.appendChild(style);
                previewDialog.value.fontFamily = fontFamily;
            }
        });

        // 图片导航相关
        const imageList = ref([]);
        const hasPrevImage = computed(() => previewDialog.value.isImage && previewDialog.value.currentImageIndex > 0);
        const hasNextImage = computed(() => previewDialog.value.isImage && previewDialog.value.currentImageIndex < imageList.value.length - 1);
        const imagePreview = ref(null);

        // 获取同级目录中的所有图片
        const getImageListInCurrentDir = () => {
            return fileList.value.filter(file => isImageFile(file.name));
        };

        // 显示上一张图片
        const showPrevImage = () => {
            if (hasPrevImage.value) {
                const prevImage = imageList.value[previewDialog.value.currentImageIndex - 1];
                updatePreviewImage(prevImage, previewDialog.value.currentImageIndex - 1);
            }
        };

        // 显示下一张图片
        const showNextImage = () => {
            if (hasNextImage.value) {
                const nextImage = imageList.value[previewDialog.value.currentImageIndex + 1];
                updatePreviewImage(nextImage, previewDialog.value.currentImageIndex + 1);
            }
        };

        // 更新预览图片
        const updatePreviewImage = (image, index) => {
            if (image) {
                previewDialog.value.currentImageIndex = index;
                previewDialog.value.title = image.name;
                previewDialog.value.content = `/raw/${image.path}`;
                previewDialog.value.currentFile = image;
            }
        };

        // 处理图片预览时的键盘事件
        const handleImageKeydown = (event) => {
            if (event.key === 'ArrowLeft') {
                showPrevImage();
            } else if (event.key === 'ArrowRight') {
                showNextImage();
            }
        };

        // 监听预览对话框显示状态
        watch(() => previewDialog.value.visible, (newVisible) => {
            if (newVisible && previewDialog.value.isImage) {
                // 当显示图片预览时，获取同级目录的图片列表
                imageList.value = getImageListInCurrentDir();
                // 设置当前图片索引
                previewDialog.value.currentImageIndex = imageList.value.findIndex(
                    img => img.path === previewDialog.value.currentFile.path
                );
                // 在下一个事件循环中聚焦图片预览区域以启用键盘事件
                nextTick(() => {
                    if (imagePreview.value) {
                        imagePreview.value.focus();
                    }
                });
            }
        });

        // 重命名文件
        const renameFile = async (file) => {
            try {
                const { value: newName } = await ElMessageBox.prompt('请输入新名称', '重命名', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    inputValue: file.name,
                    inputValidator: (value) => {
                        if (!value) {
                            return '名称不能为空';
                        }
                        if (value === file.name) {
                            return '新名称不能与原名称相同';
                        }
                        if (fileList.value.some(f => f.name === value && f.path !== file.path)) {
                            return '该名称已存在';
                        }
                        return true;
                    }
                });

                if (newName) {
                    const response = await fetch(`/api/files/${encodeURIComponent(file.path)}/rename`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            new_name: newName
                        })
                    });

                    const data = await response.json();
                    if (data.error) {
                        ElMessage.error(data.error);
                        return;
                    }

                    ElMessage.success('重命名成功');
                    await loadFiles(currentPath.value);
                }
            } catch (error) {
                if (error !== 'cancel') {
                    console.error('重命名失败:', error);
                    ElMessage.error('重命名失败');
                }
            }
        };

        return {
            fileList,
            currentPath,
            pathSegments,
            previewDialog,
            deleteDialog,
            isDragOver,
            uploadProgress,
            fileInput,
            folderInput,
            handleItemClick,
            navigateTo,
            getPathUpTo,
            saveFile,
            saveAndClose,
            showDeleteDialog,
            confirmDelete,
            isImageFile,
            isVideoFile,
            formatFileSize,
            handleFileSelect,
            handleFileDrop,
            downloadFile,
            previewText,
            hasPrevImage,
            hasNextImage,
            showPrevImage,
            showNextImage,
            handleImageKeydown,
            imagePreview,
            renameFile,
            copyFileLink,
            onTooltipHide,
            hasWritePermission,
            login,  // 暴露登录方法
        };
    }
});

// Use Element Plus
app.use(ElementPlus);
// Register all icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component);
    // console.log(key);
}
app.mount('#app');