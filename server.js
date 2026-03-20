const express = require('express');
const bodyParser = require('body-parser');
const { morph } = require('@datoplasm/morphology-ru');

const app = express();
app.use(bodyParser.json());

// Пользовательский словарь (можно дополнять)
const customDict = {
  'генеральный директор': 'генерального директора',
  'действующий на основании устава': 'действующего на основании устава',
  'индивидуальный предприниматель': 'индивидуального предпринимателя',
  'представитель по доверенности': 'представителя по доверенности'
};

// Функция склонения одного слова
function declineWord(word) {
  try {
    const forms = morph(word);
    if (forms && forms.gen) return forms.gen;
  } catch (e) {
    console.warn(`Не удалось склонить слово "${word}": ${e.message}`);
  }
  return word;
}

// Склонение фразы
function declinePhrase(text) {
  const lowerText = text.toLowerCase().trim();
  if (customDict[lowerText]) return customDict[lowerText];

  const parts = text.split(/\s+/);
  if (parts.length === 3) {
    try {
      const surname = declineWord(parts[0]);
      const name = declineWord(parts[1]);
      const patronymic = declineWord(parts[2]);
      return `${surname} ${name} ${patronymic}`;
    } catch (e) {}
  }

  const declined = parts.map(word => declineWord(word));
  return declined.join(' ');
}

// API для одного текста или массива
app.post('/decline', (req, res) => {
  const data = req.body;
  if (!data) return res.status(400).json({ error: 'no json' });

  if (data.text !== undefined) {
    const result = declinePhrase(data.text);
    return res.json({ result });
  }

  if (Array.isArray(data.texts)) {
    const results = data.texts.map(t => declinePhrase(t));
    return res.json({ results });
  }

  res.status(400).json({ error: 'invalid request' });
});

// Health check для Render
app.get('/health', (req, res) => res.send('OK'));
app.get('/', (req, res) => res.send('OK'));

const port = process.env.PORT || 3000;
app.listen(port, '0.0.0.0', () => {
  console.log(`Server is running on port ${port}`);
});
