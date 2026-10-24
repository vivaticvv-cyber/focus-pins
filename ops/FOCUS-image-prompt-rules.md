# FOCUS — правила scene_prompt для FLUX.2 klein 4B

Основа: опыт QA 24.10.2026 (M010 календарь) + официальные гайды Black Forest Labs / HF Space system prompt.

## Главное

1. **Нет негативов.** Модель не понимает «no / without / not». Фраза «no numbers» заставляет рисовать цифры-кашу.  
   Вместо «no text» → «smooth blank cream paper», «clean unmarked surface», «solid coloured band».

2. **Текст на объектах.** Если объект в реальности с текстом (календарь, вывеска, экран, бирка), а текста в кавычках нет — модель рисует бессмыслицу.  
   Либо дай точный текст в кавычках (`"MON"` / `"15"`), либо **убери объект с ожидаемым текстом** и опиши пустые поверхности.

3. **Сетки и счёт.** 7×5 grid, «five bowls», «three baskets» — слабое место klein 4B (blindspots: count).  
   Не проси точную сетку месяца. Для «календаря» лучше: один блок / одна страница / один день — без клеток.

4. **Порядок.** Subject first → детали → свет. Короткие предложения. Стиль подмешивается кодом (`medium` + `palette` без hex).

5. **Стиль.** Для простых твёрдых предметов (календарь-блок, кружка, таймер) лучше **clay3d** или **papercraft** (чёткая форма). Gouache/felt дают «живопись», сетка размазывается.

## Плохо → хорошо

| Плохо | Хорошо |
|-------|--------|
| no numbers, no writing | smooth blank cream pages with no marks |
| monthly grid of seven columns | single standing desk calendar, solid teal band on top |
| blank calendar without text | thick cream paper block, solid soft teal band across the top |
| a pair of boots | one boot beside another boot / two boots side by side (и всё равно проверять) |

## Календарь (M010 и аналоги)

Не рисовать месячную сетку. Метафора «один календарь»:

```
A single standing desk calendar on a wooden table, thick cream paper block with a solid soft teal band across the top, smooth blank cream pages with no marks, metal ring binding along the top edge, warm peach wall behind, gentle daylight from the left, everything fully visible and brightly lit
```

Style column: `clay3d`.

## После генерации

Глазами: нет лишних цифр/букв, анатомия животных, счёт предметов. Брак → status=new, удалить jpg, упростить сцену по этим правилам.
