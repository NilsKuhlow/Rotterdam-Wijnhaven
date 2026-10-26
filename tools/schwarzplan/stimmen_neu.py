# -*- coding: utf-8 -*-
"""Die Stimmen aus dem Viertel sauber formulieren.

Die Notizen aus den Gespraechen sind seinerzeit in alle drei Sprachen
uebernommen worden, wie sie im Block standen: in Satzfragmenten, mit
woertlich uebersetzten Wendungen ("die Gedanken fliegen lassen",
"Industriegeschaeft" fuer industrial business) und mit einem falschen
Geschlecht ("Die Wijnhaven ist ein Bezirk").

Hier wird nur die Form berichtigt, nicht die Aussage. Jede Stimme sagt
nachher dasselbe wie vorher, nur in ganzen Saetzen und in Wendungen,
die es in der jeweiligen Sprache wirklich gibt.

Dazu die Schreibweise des Namens: Boaz, nicht Boars. Das betrifft auch
die Kennung, denn an ihr haengt die Sprechblase im Stadtmodell.
"""
import io

R = (r"C:\Users\nils\OneDrive\ARCHITEKTUR\01_PROJEKTE\STUDIUM"
     r"\2026_WS2627_HochschuleWismar\WPM STADT + RAUM\Output"
     r"\Rotterdam-Wijnhaven\index.html")

ALT = """var STIMMEN = [
  { id:'shyvanna', who:'Shyvanna', pos:'150m 74m -180m',
    ctx:{ de:'', nl:'', en:'' },
    q:{ de:'Die Wijnhaven ist ein Bezirk, in dem weniger gelebt als gearbeitet wird. Kein Ort der Ruhe, eher ein Ort des Alltags.',
        nl:'De Wijnhaven is een wijk waar minder wordt gewoond dan gewerkt. Geen plek van rust, eerder een plek van alledag.',
        en:'Wijnhaven is a district where there is less living than working. Not a place of rest, more a place of everyday life.' } },

  { id:'boars', who:'Boars', pos:'140m 74m -110m',
    ctx:{ de:'seit vier Jahren in Rotterdam', nl:'vier jaar in Rotterdam', en:'four years in Rotterdam' },
    q:{ de:'Die Hochschule macht den gr\u00f6\u00dften Teil aus. Eine Industriestra\u00dfe, nicht die sch\u00f6nste. Zu teuer, und dadurch eine gro\u00dfe Trennung zwischen jungen Leuten und gro\u00dfen Unternehmen. Identit\u00e4ten gehen hier verloren.',
        nl:'De hogeschool is het grootste deel. Een industriestraat, niet de mooiste. Te duur, en daardoor een grote scheiding tussen jonge mensen en grote bedrijven. Identiteiten gaan hier verloren.',
        en:'The school is the biggest part. An industrial street, not the prettiest. Too expensive, and so a big separation between young people and big companies. Identities get lost here.' } },

  { id:'patrick', who:'Patrick', pos:'230m 74m -300m',
    ctx:{ de:'gerade zugezogen', nl:'net verhuisd', en:'just moved here' },
    q:{ de:'Es kann wie eine feindliche Gegend wirken. Zugleich ist da Vertrautheit, wegen der Leute aus der Hochschule. Gro\u00dfe Geb\u00e4ude, in denen man die Gedanken fliegen lassen kann.',
        nl:'Het kan overkomen als een vijandige omgeving. Tegelijk is er vertrouwdheid, door de mensen van de hogeschool. Grote gebouwen waarin je je gedachten kunt laten gaan.',
        en:'It can look like a hostile area. At the same time there is comfort, because of the school people here. Big buildings where you can let your thoughts fly.' } },

  { id:'sirano', who:'Sirano', pos:'95m 74m -330m',
    ctx:{ de:'erstes Studienjahr', nl:'eerste studiejaar', en:'first year' },
    q:{ de:'Das gro\u00dfe Industriegesch\u00e4ft versucht, einem die Identit\u00e4t zu nehmen; die Hochschule ist der Brennpunkt, an dem sie noch da ist. Den Hafen in ein Wohnquartier zu verwandeln, ist gescheitert: Es fehlen Farbe und Kultur, Parks zum Beispiel.',
        nl:'Het grote industri\u00eble bedrijfsleven probeert je je identiteit af te nemen; de hogeschool is het brandpunt waar die er nog is. De haven omvormen tot woonwijk is mislukt: kleur en cultuur ontbreken, parken bijvoorbeeld.',
        en:'The big industrial business is trying to take away your identity; the school is the hotspot where it is still there. Transforming the harbour into a housing project has failed, since it lacks colour and culture, parks for example.' } },

  { id:'timo-nora-diana', who:'Timo, Nora, Diana', pos:'220m 74m -400m',
    ctx:{ de:'erstes Studienjahr', nl:'eerste studiejaar', en:'first year' },
    q:{ de:'Eine Person aus der Gruppe lebt ihr ganzes Leben in Rotterdam und war noch nie auf dem Wijnhaveneiland. Der Blaak dagegen ist ein architektonischer Erfolg. Hierher w\u00fcrden wir mit Freunden nicht gehen.',
        nl:'Iemand uit de groep woont haar hele leven in Rotterdam en is nog nooit op het Wijnhaveneiland geweest. De Blaak is daarentegen een architectonisch succes. Hierheen zouden wij niet met vrienden gaan.',
        en:'One of the group has lived in Rotterdam their whole life and has never been to the Wijnhaveneiland. The Blaak, by contrast, is an architectural success. We would not come here with friends.' } },
];"""

NEU = """var STIMMEN = [
  { id:'shyvanna', who:'Shyvanna', pos:'150m 74m -180m',
    ctx:{ de:'', nl:'', en:'' },
    q:{ de:'Am Wijnhaven wird weniger gewohnt als gearbeitet. Kein Ort der Ruhe, eher einer des Alltags.',
        nl:'Aan de Wijnhaven wordt minder gewoond dan gewerkt. Geen plek van rust, eerder een plek van alledag.',
        en:'At the Wijnhaven there is less living than working. Not a place of rest, more one of everyday life.' } },

  { id:'boaz', who:'Boaz', pos:'140m 74m -110m',
    ctx:{ de:'seit vier Jahren in Rotterdam', nl:'vier jaar in Rotterdam', en:'four years in Rotterdam' },
    q:{ de:'Das Viertel geh\u00f6rt vor allem der Hochschule. Eine Industriestra\u00dfe, nicht die sch\u00f6nste, und zu teuer. Das trennt die jungen Leute von den gro\u00dfen Unternehmen, und Identit\u00e4t geht dabei verloren.',
        nl:'De wijk is vooral van de hogeschool. Een industriestraat, niet de mooiste, en te duur. Dat scheidt de jonge mensen van de grote bedrijven, en identiteit gaat daarbij verloren.',
        en:'The district belongs mostly to the university. An industrial street, not the prettiest, and too expensive. That separates the young people from the big companies, and identity gets lost along the way.' } },

  { id:'patrick', who:'Patrick', pos:'230m 74m -300m',
    ctx:{ de:'gerade zugezogen', nl:'net verhuisd', en:'just moved here' },
    q:{ de:'Die Gegend kann abweisend wirken. Vertraut wird sie durch die Leute von der Hochschule. Und es sind gro\u00dfe Geb\u00e4ude, bei denen man den Gedanken freien Lauf lassen kann.',
        nl:'De omgeving kan afwijzend overkomen. Vertrouwd wordt ze door de mensen van de hogeschool. En het zijn grote gebouwen, waarbij je je gedachten de vrije loop kunt laten.',
        en:'The area can feel unwelcoming. What makes it familiar are the people from the university. And they are big buildings, the kind that let your thoughts run free.' } },

  { id:'sirano', who:'Sirano', pos:'95m 74m -330m',
    ctx:{ de:'erstes Studienjahr', nl:'eerste studiejaar', en:'first year' },
    q:{ de:'Die gro\u00dfen Unternehmen nehmen einem die Identit\u00e4t, und die Hochschule ist der eine Ort, an dem sie noch da ist. Den Hafen in ein Wohnquartier zu verwandeln, ist misslungen: Es fehlen Farbe und Kultur, Parks zum Beispiel.',
        nl:'De grote bedrijven nemen je je identiteit af, en de hogeschool is de ene plek waar die er nog is. De haven omvormen tot woonwijk is mislukt: kleur en cultuur ontbreken, parken bijvoorbeeld.',
        en:'The big companies take your identity away, and the university is the one place where it is still there. Turning the harbour into a residential quarter has failed: colour and culture are missing, parks for example.' } },

  { id:'timo-nora-diana', who:'Timo, Nora, Diana', pos:'220m 74m -400m',
    ctx:{ de:'erstes Studienjahr', nl:'eerste studiejaar', en:'first year' },
    q:{ de:'Eine von uns wohnt schon immer in Rotterdam und war noch nie auf dem Wijnhaveneiland. Der Blaak dagegen ist ein architektonischer Erfolg. Hierher w\u00fcrden wir mit Freunden nicht gehen.',
        nl:'Een van ons woont hier al altijd en is nog nooit op het Wijnhaveneiland geweest. De Blaak is daarentegen een architectonisch succes. Hierheen zouden we niet met vrienden gaan.',
        en:'One of us has always lived in Rotterdam and has never been to the Wijnhaveneiland. The Blaak, by contrast, is an architectural success. We would not come here with friends.' } },
];"""


def main():
    s = io.open(R, encoding='utf-8-sig').read()
    assert s.count(ALT) == 1, 'Stimmenblock nicht gefunden'
    s = s.replace(ALT, NEU)
    assert 'Boars' not in s and "'boars'" not in s
    io.open(R, 'w', encoding='utf-8-sig', newline='\r\n').write(s)
    print('Stimmen neu gefasst, Boaz berichtigt')


if __name__ == '__main__':
    main()
