document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.like-btn, .dislike-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const commentId = this.dataset.commentId;
            const value = parseInt(this.dataset.value);
            const articleSlug = document.getElementById('article-data').dataset.slug; // Добавляем slug статьи

            console.log('Initiating reaction for comment:', commentId, 'value:', value); // Логирование

            fetch(`/articles/${encodeURIComponent(articleSlug)}/comment/${commentId}/react/`, { // Добавляем slug в URL
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `value=${value}`
            })
            .then(response => {
                if(!response.ok) throw new Error('Network error');
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data); // Логирование ответа
                const commentElement = document.querySelector(`[data-comment-id="${commentId}"]`);
                
                // Обновление счетчиков
                const likeCount = commentElement.querySelector('.like-btn .count');
                const dislikeCount = commentElement.querySelector('.dislike-btn .count');
                likeCount.textContent = data.likes;
                dislikeCount.textContent = data.dislikes;

                // Обновление состояний
                const likeBtn = commentElement.querySelector('.like-btn');
                const dislikeBtn = commentElement.querySelector('.dislike-btn');
                
                likeBtn.classList.remove('active-like');
                dislikeBtn.classList.remove('active-dislike');

                if(data.user_reaction === 1) {
                    likeBtn.classList.add('active-like');
                } else if(data.user_reaction === -1) {
                    dislikeBtn.classList.add('active-dislike');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при обновлении реакции');
            });
        });
    });

    document.querySelectorAll('.delete-comment-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const commentElement = this.closest('.comment');
            const commentId = commentElement.dataset.commentId;
            const articleSlug = document.getElementById('article-data').dataset.slug;
            
            console.log('Slug:', articleSlug); // Для проверки
            console.log('Comment ID:', commentId); // Для проверки

            if(commentId && articleSlug && confirm('Вы уверены, что хотите удалить комментарий?')) {
                const url = `/articles/${encodeURIComponent(articleSlug)}/comment/${commentId}/delete/`;
                console.log('Request URL:', url); // Для проверки
                
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                })
                .then(response => {
                    if(response.ok) {
                        commentElement.remove();
                    } else {
                        console.error('Delete error:', response.status);
                    }
                })
                .catch(error => console.error('Fetch error:', error));
            }
        });
    });

    // Обработчик редактирования комментария
    document.querySelectorAll('.edit-comment-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const commentElement = this.closest('.comment');
            const commentId = commentElement.dataset.commentId;
            const contentElement = commentElement.querySelector('.comment-content');
            const originalText = contentElement.textContent;

            // Создаем текстовую область для редактирования
            const textarea = document.createElement('textarea');
            textarea.className = 'edit-comment-textarea';
            textarea.value = originalText;
            
            // Заменяем контент на textarea
            contentElement.replaceWith(textarea);

            // Создаем кнопки подтверждения/отмены
            const saveBtn = document.createElement('button');
            saveBtn.className = 'save-edit-btn';
            saveBtn.innerHTML = '<i class="fas fa-check"></i> Сохранить';
            
            const cancelBtn = document.createElement('button');
            cancelBtn.className = 'cancel-edit-btn';
            cancelBtn.innerHTML = '<i class="fas fa-times"></i> Отмена';

            // Вставляем кнопки после textarea
            textarea.insertAdjacentElement('afterend', saveBtn);
            textarea.insertAdjacentElement('afterend', cancelBtn);

            // Обработчик сохранения
            saveBtn.addEventListener('click', () => {
                fetch(`/articles/comment/${commentId}/edit/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: `text=${encodeURIComponent(textarea.value)}`
                })
                .then(response => response.json())
                .then(data => {
                    if(data.success) {
                        contentElement.textContent = data.new_text;
                        textarea.replaceWith(contentElement);
                        saveBtn.remove();
                        cancelBtn.remove();
                    }
                });
            });

            // Обработчик отмены
            cancelBtn.addEventListener('click', () => {
                textarea.replaceWith(contentElement);
                saveBtn.remove();
                cancelBtn.remove();
            });
        });
    });
});

