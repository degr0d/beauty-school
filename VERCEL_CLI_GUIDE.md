# 🚀 Быстрая инструкция: Деплой через Vercel CLI

## Имя проекта

**Имя вашего проекта в Vercel:** `beauty-school`

## Что вводить в CLI

Когда Vercel спрашивает:
```
? Link to existing project? yes
? What's the name of your existing project?
```

**Введите:** `beauty-school`

## Полная последовательность команд

```bash
cd frontend
vercel --prod
```

Или интерактивно:
```bash
cd frontend
vercel
```

**Ответы на вопросы:**
1. `Set up and deploy?` → **yes**
2. `Which scope?` → **dima's projects** (или ваш scope)
3. `Link to existing project?` → **yes**
4. `What's the name of your existing project?` → **beauty-school** ← ВОТ ЭТО!
5. `In which directory is your code located?` → **./** (просто Enter)
6. `Want to override the settings?` → **N** (или Enter)

## Альтернатива: Деплой без привязки

Если хотите создать новый деплой без привязки к существующему проекту:

```bash
cd frontend
vercel --prod
```

И на вопрос `Link to existing project?` ответьте **no**

Но лучше использовать существующий проект `beauty-school` чтобы все деплои были в одном месте.

