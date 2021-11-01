import requests
from itertools import cycle

instagram_embed_colours = cycle([
    0xcd486b,
    0xfbad50,
    0xfccc63,
    0xbc2a8d,
    0xe95950,
    0x8a3ab9,
    0x4c68d7
])

instagram_usernames = ['_sour_candy_', '_techwarts', 'aatmatrisha_', 'acmpesuecc',
                       'acmw.pesu', 'aikya_pesu',
                       'apostrophe.pesuecc', 'ayra_the.helping.hand_pesu',
                       'blueprint_pesuecc', 'c.o.d.s_community', 'c.o.d.s_pesu_ecc',
                       'c.o.d.s_pesu_rr', 'cie.pesu', 'clubs_pesuecc', 'codechef_pesuecc',
                       'csr.pesu', 'dscpesu.ec', 'dscpesu.rr', 'dsgnr_pesu',
                       'dsgnr_pesuecc', 'entrepreneurshipclub.pes', 'equinox.pes', 'equinox.pesecc',
                       'grimmreaders_pesu', 'hayaracing', 'humans_of_pes', 'humans_of_pesu',
                       'ieee.ras.pesu', 'ieee.ras.pesuecc', 'ieee_pes_sscs_photonics', 'ieeepesit',
                       'ingeniushackathon', 'kludge_pesu', 'linguista.club',
                       'maayapesu', 'mangobites.pesu', 'munsoc.pesecc', 'newolfsociety',
                       'ninaada.pesu', 'parallax_techwarts', 'pes.epsilon', 'pes.lab', 'pes.opensource',
                       'pes.qforest', 'pes.spacejam', 'pes_ecell', 'pesdebsoc',
                       'peshackerspace', 'peshackerspace.ecc', 'pesmunsociety', 'pesu.gdc',
                       'pesu.hashtagcrew', 'pesu.io', 'pesu.tas',
                       'pesu_covid_support', 'pesu_nirantara', 'pesuniversity', 'pixelloid_pes',
                       'pixels.pesu', 'quotientquizclub', 'rc_pesu3190', 'saarang_official',
                       'samarpana.india', 'shakennotstirred.pes', 'swarantraka.pes', 'team.encore',
                       'team_aeolus', 'teamsanskrithi', 'techplussocialgoodpesu', 'tedxpesu',
                       'tedxpesuecc', 'tensor.pesu', 'the_changemakers_society', 'the_clefhangers',
                       'thealcodingclub', 'thebisibelebois', 'themusicclubpesu', 'thenautankiteam',
                       'thor_pesu', 'throughthelens.pesu', 'trance_pes', 'under25pes', 'under25pesuecc',
                       'vegaracingelectric', 'writeangle.pesu', 'zeroday.pesuecc', 'adconnect_pesu', 'cognitivemd_pesu',
                       'appex.pesu', 'adgpesu', 'pesumeraki_fc', 'pesuventurelabs', 'terpsichore_pesu', 'panachepesuecc',
                       'isfcr.pesu', 'abhyudaya.pesu', 'thecoderfactory_pesu', 'etal.pesu', 'hallothon.pesu', 'gamedev_pesu']


def getLastPhotoDate(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["taken_at_timestamp"]


def getPhotoDescription(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"]


def getLastThumbnailURL(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["thumbnail_src"]


def getPostLink(html):
    return f'https://www.instagram.com/p/{html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["shortcode"]}'


def checkVideo(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["is_video"]


def getVideoURL(html):
    return html.json()["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"][0]["node"]["video_url"]


def getInstagramHTML(INSTAGRAM_USERNAME):
    headers = {
        "Host": "www.instagram.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
    }
    html = requests.get("https://www.instagram.com/" +
                        INSTAGRAM_USERNAME + "/feed/?__a=1", headers=headers)
    return html
