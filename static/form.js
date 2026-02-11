const mealCountSelect = document.getElementById('meal_count');
const mealFields = document.getElementById('meal-fields');

function createMealField(index) {
  const wrapper = document.createElement('div');
  wrapper.className = 'field';

  const label = document.createElement('label');
  label.setAttribute('for', `meal_${index}`);
  label.textContent = `Maaltijd ${index} (verplicht)`;

  const input = document.createElement('textarea');
  input.id = `meal_${index}`;
  input.name = `meal_${index}`;
  input.required = true;
  input.rows = 2;
  input.placeholder = 'Bijv. 2 volkoren boterhammen met kaas, thee met zoetje, ketchup...';

  wrapper.appendChild(label);
  wrapper.appendChild(input);
  return wrapper;
}

function renderMealFields() {
  mealFields.innerHTML = '';
  const count = Number(mealCountSelect.value || 0);

  for (let i = 1; i <= count; i += 1) {
    mealFields.appendChild(createMealField(i));
  }
}

mealCountSelect.addEventListener('change', renderMealFields);
