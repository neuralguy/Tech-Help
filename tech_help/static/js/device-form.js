document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('specificationsContainer');
    const addButton = document.getElementById('addSpecification');
    const form = document.getElementById('deviceForm');
    const specsInput = document.querySelector('input[name="specifications"]');
    
    // Загружаем существующие спецификации при редактировании
    let specs = [];
    try {
        specs = JSON.parse(specsInput.value || '[]');
    } catch (e) {
        console.error('Failed to parse specifications:', e);
    }
    
    // Создаем поля для существующих спецификаций
    specs.forEach(spec => addSpecificationField(spec));
    
    // Обработчик добавления новой спецификации
    addButton.addEventListener('click', () => addSpecificationField());
    
    // Обработчик отправки формы
    form.addEventListener('submit', function(e) {
        const specs = [];
        container.querySelectorAll('.specification-row').forEach(row => {
            const name = row.querySelector('[name="spec_name"]').value;
            const value = row.querySelector('[name="spec_value"]').value;
            const unit = row.querySelector('[name="spec_unit"]').value;
            
            if (name && value) {
                specs.push({ name, value, unit });
            }
        });
        
        specsInput.value = JSON.stringify(specs);
    });
    
    function addSpecificationField(spec = null) {
        const row = document.createElement('div');
        row.className = 'specification-row grid grid-cols-1 md:grid-cols-3 gap-4';
        
        // Создаем datalist для автозаполнения
        const datalistId = `specs-${Date.now()}`;
        const datalist = document.createElement('datalist');
        datalist.id = datalistId;
        existingSpecs.forEach(spec => {
            const option = document.createElement('option');
            option.value = spec.name;
            option.dataset.unit = spec.unit;
            datalist.appendChild(option);
        });
        
        row.innerHTML = `
            <div>
                <input type="text" 
                       name="spec_name" 
                       class="form-input" 
                       placeholder="Название"
                       list="${datalistId}"
                       value="${spec ? spec.name : ''}"
                       onchange="updateUnit(this)">
                ${datalist.outerHTML}
            </div>
            <div>
                <input type="text" 
                       name="spec_value" 
                       class="form-input" 
                       placeholder="Значение"
                       value="${spec ? spec.value : ''}">
            </div>
            <div class="flex gap-2">
                <input type="text" 
                       name="spec_unit" 
                       class="form-input" 
                       placeholder="Единица измерения"
                       value="${spec ? spec.unit : ''}">
                <button type="button" 
                        class="btn-secondary text-red-500"
                        onclick="this.closest('.specification-row').remove()">
                    ×
                </button>
            </div>
        `;
        
        container.appendChild(row);
    }
    
    // Функция для автозаполнения единицы измерения
    window.updateUnit = function(input) {
        const option = Array.from(input.list.options).find(opt => opt.value === input.value);
        if (option) {
            const row = input.closest('.specification-row');
            const unitInput = row.querySelector('[name="spec_unit"]');
            unitInput.value = option.dataset.unit;
        }
    };
}); 