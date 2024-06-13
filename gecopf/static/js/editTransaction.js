document.addEventListener('DOMContentLoaded', function() {
    const editButtons = document.querySelectorAll('.btn-edit');
    const editForm = document.getElementById('transactionForm');
    const editTransactionId = document.getElementById('editTransactionId');
    const editTransactionName = document.getElementById('editTransactionName');
    const editTransactionConcept = document.getElementById('editTransactionConcept');
    const editTransactionAmount = document.getElementById('editTransactionAmount');

    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Obtener datos de la transacción para editar
            const transactionId = this.getAttribute('data-transaction-id');
            const transactionName = this.getAttribute('data-transaction-name');
            const transactionConcept = this.getAttribute('data-transaction-concept');
            const transactionAmount = this.getAttribute('data-transaction-amount');
            
            // Asignar datos al formulario de edición
            editTransactionId.value = transactionId;
            editTransactionName.value = transactionName;
            editTransactionConcept.value = transactionConcept;
            editTransactionAmount.value = parseFloat(transactionAmount);
        });
    });

    editForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const actionUrl = this.getAttribute('action');
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Construir un objeto JSON con los datos del formulario
        const jsonData = {
            action: 'edit',
            transaction_id: editTransactionId.value,
            name: editTransactionName.value,
            concept: editTransactionConcept.value,
            amount: editTransactionAmount.value
        };

        fetch(actionUrl, {
            method: 'POST',
            body: JSON.stringify(jsonData), // Convertir el objeto JSON a una cadena
            headers: {
                'Content-Type': 'application/json', // Especificar el tipo de contenido como JSON
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken // Incluir el token CSRF como encabezado
            }
        })
        .then(response => {
            // Verificar si la respuesta es OK
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            // Verificar el tipo de contenido de la respuesta
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                // Si es JSON, analizar la respuesta como tal
                return response.json();
            } else if (contentType && contentType.includes('text/html')) {
                // Si es HTML, leer la respuesta como texto
                return response.text();
            } else {
                // Si no es JSON, devolver una cadena vacía
                return '';
            }
        })

        .then(data => {
            // Verificar si la respuesta es un objeto JSON o una cadena vacía
            if (data && typeof data === 'object') {
                // Manejar la respuesta JSON
                if (data.success) {
                    location.reload(); // Recargar la página para ver los cambios
                } else {
                    console.error('Error:', data.error);
                }
            } else if (data && typeof data === 'string') {
                // Si es una cadena de texto, manejar la respuesta HTML
                location.reload(); // Recargar la página para ver los cambios
            } else {
                // Manejar la respuesta no JSON
                console.log('Respuesta no JSON:', data);
                // Aquí puedes manejar la respuesta no JSON según sea necesario
            }
        })

        .catch(error => {
            console.error('Error en la solicitud:', error);
        });  

        $('#editTransactionModal').modal('hide'); // Ocultar modal después de guardar
    });
});

window.addEventListener('load', function() {
    var cantidadInput = document.getElementById('editTransactionAmount');

    formatAmount(cantidadInput);

    cantidadInput.addEventListener('change', function() {
        formatAmount(this);
    });

    function formatAmount(input) {
        // Obtener el valor actual del campo
        var value = input.value;
        
        // Verificar si el valor ya tiene decimales
        if (value.indexOf('.') === -1) {
            // Si no tiene decimales, aplicar el formateo a dos decimales
            var floatValue = parseFloat(value);
            if (!isNaN(floatValue)) {
                input.value = floatValue.toFixed(2);
            }
        }
    }
});