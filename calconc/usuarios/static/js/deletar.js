const btnDeletar = document.querySelectorAll('.btn-deletar');
        btnDeletar.forEach(button => {
            button.addEventListener('click', () => {
                const id = button.getAttribute('data-id');
                console.log('ID:', id);

                const confirmDelete = confirm('Tem certeza que deseja excluir?');
                console.log('Confirm Delete:', confirmDelete);

                if (confirmDelete) {
                    const url = button.getAttribute('data-url');
                    console.log('URL:', url);

                    const csrfToken = document.cookie.match(/csrftoken=([^ ;]+)/)[1];
                    console.log('CSRF Token:', csrfToken);

                    fetch(url, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken
                        }
                    })
                    .then(response => {
                        if (response.ok) {
                            console.log('Registro excluído com sucesso');
                            location.reload();
                        } else {
                            console.error('Erro ao excluir registro');
                        }
                    })
                    .catch(error => {
                        console.error('Erro ao excluir registro:', error);
                    });
                }
            });
        });