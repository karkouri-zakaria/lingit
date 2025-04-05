def colorize_noun(flashcard, colors={("der", "(der)"): "DeepSkyBlue", ("die", "(die)"): "DeepPink", ("das", "(das)"): "LawnGreen"}): 
    words = flashcard["Target"].split()
    color_map = {a: c for arts, c in colors.items() for a in arts}
    for i, w in enumerate(words[:-1]): 
        if w.lower() in color_map: words[i+1] = f'<span style="color: {color_map[w.lower()]};">{words[i+1]}</span>'
    if flashcard["Source"][:3] == "to ":
        for i, w in enumerate(words):
            if '<span' in w or w.lower() in color_map: continue
            words[i] = f'<span style="color: yellow;">{w.split("·",1)[0]}</span>·<span style="color: orange;">{w.split("·",1)[1]}</span>' if "·" in w else f'<span style="color: orange;">{w}</span>'
    return " ".join(words)  