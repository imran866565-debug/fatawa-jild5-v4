#!/usr/bin/env python3
"""Merge Fatawa Razviya Jild 5 easy-Urdu tashreeh v4 chunks into jild-05.json.

Reads the 14 chunk files listed in chunks-manifest-v4-jild05.json,
concatenates them in order 01 -> 14, renames the second occurrences of
the two duplicated masala numbers (see RENAME QUIRK below), derives
start_page = min(pages) where the field is absent, normalises page
markers, validates, and writes {"masail": [...]} to jild-05.json.

ORDER -- chunk order is the order (no quirk, unlike Jild 1 Part 2):
  The v3 merged file ~/workspace/fatawa-app/content/tashreeh/jild-05.json
  has ID order == concatenation order of the v4 chunks 01..14 (verified
  locally by the coordinator: all 209 ids match the v3 sequence exactly
  after the renames). Do NOT sort or reorder. Within each chunk, items
  keep file order.

RENAME QUIRK: the book numbers TWO different masail 263 and TWO
  different masail 304. The v3 merged file disambiguates the second
  occurrences by appending the start page: chunk-09
  jild5-masala-263 (pp. 413-414, اقامت میں دائیں بائیں رخ کرنا) ->
  jild5-masala-263-p413; chunk-09 jild5-masala-304 (p. 427, مسجد میں
  پنجوقتہ اذان کی اہمیت) -> jild5-masala-304-p427. The first occurrences
  stay plain (263 pp. 117-118 chunk 02; 304 pp. 328-329 chunk 07). The
  merge renames the SECOND occurrence of any duplicated id to
  {id}-p{start_page} and asserts exactly those two renames happen.

START_PAGE: every one of the 14 v4 chunks carries start_page ==
  min(pages) for all its items (verified by the coordinator). The
  derivation code below stays as a safety net; it is expected to
  derive 0 items.

MARKER NORMALISATION (the only text transformation): page markers, if
  present, are normalised to the single form [safha N] written with the
  Urdu word for page:
  - lenticular-bracket form (U+3010/U+3011 around the Urdu word for
    page + number) -> [safha N]
  - [short form] -> [safha N]
  - [safha N] stays as-is
  Applied to every string field of every item (jawab, sawal, title,
  notes). The 14 v4 chunks contain ZERO markers of any form (verified
  locally), so normalisation is expected to be a no-op here; the code
  stays so the merge is robust and the "none remain" assertions still
  run. No other text is touched and no markers are invented.
  NOTE: the literal lenticular-bracket characters are written here only
  as U+3010/U+3011 escapes, never as literal characters in this file.

VALIDATION (fails loudly on any violation):
  209 items; ID sequence EXACTLY == the v3 merged file's ID sequence
  (embedded below as V3_IDS, copied verbatim from
  ~/workspace/fatawa-app/content/tashreeh/jild-05.json); pages per item
  identical to v3 (embedded as V3_PAGES, same source, verified against
  the v3 file before pushing); 645 unique pages (min 5, max 694);
  volume_ids == {36}; start_page == min(pages) for every item (after
  derivation); zero empty tashreeh_jawab; no lenticular / short markers
  remain; first id jild5-p5, last id jild5-p681.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = "chunks-manifest-v4-jild05.json"

# Concatenation order: chunk files 01 -> 14, in order.
CHUNK_ORDER = [f"jild-05-chunk-{n:02d}.json" for n in range(1, 15)]

EXPECTED_ITEMS = 209
EXPECTED_PAGES = 645
EXPECTED_MIN_PAGE = 5
EXPECTED_MAX_PAGE = 694
EXPECTED_VOLUME_IDS = {36}
EXPECTED_FIRST_ID = "jild5-p5"
EXPECTED_LAST_ID = "jild5-p681"

# v3 ID sequence, verbatim from content/tashreeh/jild-05.json.
V3_IDS = ['jild5-p5', 'jild5-masala-249', 'jild5-masala-250', 'jild5-masala-251', 'jild5-masala-252', 'jild5-masala-253', 'jild5-masala-254', 'jild5-masala-255', 'jild5-masala-256', 'jild5-p114', 'jild5-masala-257', 'jild5-masala-260', 'jild5-masala-261', 'jild5-masala-262', 'jild5-masala-263', 'jild5-masala-265', 'jild5-masala-266', 'jild5-masala-267', 'jild5-masala-268', 'jild5-masala-269', 'jild5-masala-270', 'jild5-masala-271', 'jild5-masala-272', 'jild5-masala-273', 'jild5-masala-274', 'jild5-masala-275', 'jild5-masala-277', 'jild5-masala-278', 'jild5-masala-279', 'jild5-masala-280', 'jild5-masala-281', 'jild5-masala-282', 'jild5-masala-284', 'jild5-masala-286', 'jild5-p168', 'jild5-p175', 'jild5-p182', 'jild5-p187', 'jild5-p189', 'jild5-p197', 'jild5-p204', 'jild5-p210', 'jild5-p211', 'jild5-p215', 'jild5-p216', 'jild5-p221', 'jild5-p222', 'jild5-p228', 'jild5-p233', 'jild5-p244', 'jild5-p246', 'jild5-p247', 'jild5-p253', 'jild5-p259', 'jild5-p260', 'jild5-p262', 'jild5-p266', 'jild5-p271', 'jild5-p275', 'jild5-p285', 'jild5-p289', 'jild5-p291', 'jild5-p295', 'jild5-p302', 'jild5-p310', 'jild5-masala-287', 'jild5-masala-288', 'jild5-masala-289', 'jild5-masala-290', 'jild5-masala-292', 'jild5-masala-297', 'jild5-masala-298', 'jild5-masala-299', 'jild5-masala-300', 'jild5-masala-301', 'jild5-masala-302', 'jild5-masala-303', 'jild5-masala-304', 'jild5-masala-305', 'jild5-masala-306', 'jild5-masala-307', 'jild5-masala-308', 'jild5-masala-309', 'jild5-masala-310', 'jild5-masala-311', 'jild5-masala-312', 'jild5-masala-313', 'jild5-masala-314', 'jild5-masala-315', 'jild5-masala-316', 'jild5-masala-317', 'jild5-masala-318', 'jild5-masala-319', 'jild5-masala-320', 'jild5-masala-321', 'jild5-masala-322', 'jild5-masala-323', 'jild5-masala-324', 'jild5-masala-325', 'jild5-masala-326', 'jild5-masala-327', 'jild5-masala-328', 'jild5-masala-329', 'jild5-masala-330', 'jild5-masala-331', 'jild5-masala-332', 'jild5-masala-333', 'jild5-masala-334', 'jild5-masala-335', 'jild5-masala-336', 'jild5-masala-337', 'jild5-masala-338', 'jild5-masala-339', 'jild5-masala-340', 'jild5-masala-341', 'jild5-masala-342', 'jild5-masala-343', 'jild5-masala-344', 'jild5-masala-345', 'jild5-masala-346', 'jild5-masala-347', 'jild5-masala-348', 'jild5-masala-349', 'jild5-masala-350', 'jild5-masala-351', 'jild5-masala-352', 'jild5-masala-353', 'jild5-masala-354', 'jild5-masala-455', 'jild5-p399', 'jild5-masala-356', 'jild5-masala-357', 'jild5-masala-358', 'jild5-masala-359', 'jild5-masala-360', 'jild5-masala-361', 'jild5-masala-263-p413', 'jild5-masala-364', 'jild5-masala-366', 'jild5-masala-367', 'jild5-masala-368', 'jild5-masala-369', 'jild5-masala-370', 'jild5-masala-371', 'jild5-masala-372', 'jild5-masala-373', 'jild5-masala-374', 'jild5-masala-375', 'jild5-masala-376', 'jild5-masala-377', 'jild5-masala-378', 'jild5-masala-379', 'jild5-masala-380', 'jild5-masala-381', 'jild5-masala-382', 'jild5-masala-383', 'jild5-masala-304-p427', 'jild5-masala-385', 'jild5-masala-386', 'jild5-p436', 'jild5-p443', 'jild5-p449', 'jild5-p451', 'jild5-p452', 'jild5-p454', 'jild5-p455', 'jild5-p456', 'jild5-p457', 'jild5-p461', 'jild5-p469', 'jild5-p473', 'jild5-p475', 'jild5-p476', 'jild5-p476b', 'jild5-p478', 'jild5-p479', 'jild5-p482', 'jild5-p488', 'jild5-p491', 'jild5-p496', 'jild5-p503', 'jild5-p507', 'jild5-p524', 'jild5-p527', 'jild5-p529', 'jild5-p540', 'jild5-p551', 'jild5-p554', 'jild5-p558', 'jild5-p564', 'jild5-p574', 'jild5-p577', 'jild5-p579', 'jild5-p583', 'jild5-p585', 'jild5-p589', 'jild5-p598', 'jild5-p598-2', 'jild5-p600', 'jild5-p603', 'jild5-p604', 'jild5-p606', 'jild5-p608', 'jild5-p617', 'jild5-p619', 'jild5-p623', 'jild5-masala-387', 'jild5-masala-388', 'jild5-p681']

# v3 pages per item id, verbatim from content/tashreeh/jild-05.json.
V3_PAGES = {
"jild5-p5": [5, 6],
"jild5-masala-249": [43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73],
"jild5-masala-250": [74, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97],
"jild5-masala-251": [97, 98, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
"jild5-masala-252": [109, 110],
"jild5-masala-253": [110, 111],
"jild5-masala-254": [111],
"jild5-masala-255": [111, 112],
"jild5-masala-256": [112, 113, 114],
"jild5-p114": [114],
"jild5-masala-257": [114, 115, 116],
"jild5-masala-260": [116],
"jild5-masala-261": [116],
"jild5-masala-262": [116, 117],
"jild5-masala-263": [117, 118],
"jild5-masala-265": [118, 119],
"jild5-masala-266": [119],
"jild5-masala-267": [119, 120, 121],
"jild5-masala-268": [121],
"jild5-masala-269": [122, 123, 124, 125, 126, 127],
"jild5-masala-270": [127, 128, 129, 130, 131],
"jild5-masala-271": [131, 132],
"jild5-masala-272": [132, 133],
"jild5-masala-273": [133, 134, 135, 136, 137],
"jild5-masala-274": [137, 138, 139, 140],
"jild5-masala-275": [140, 141],
"jild5-masala-277": [141, 142, 143, 144, 145, 146, 147, 148, 149],
"jild5-masala-278": [149, 150, 151, 152],
"jild5-masala-279": [152, 153, 154],
"jild5-masala-280": [154],
"jild5-masala-281": [154, 155, 156],
"jild5-masala-282": [157, 158],
"jild5-masala-284": [158, 159],
"jild5-masala-286": [160, 161, 162, 163, 164, 165, 166, 167],
"jild5-p168": [168, 169, 170, 171, 172, 173, 174, 175],
"jild5-p175": [175, 176, 177, 178, 179, 180, 181],
"jild5-p182": [182, 183, 184, 185, 186, 187],
"jild5-p187": [187, 188, 189],
"jild5-p189": [189, 190, 191, 192, 193, 194, 195, 196, 197],
"jild5-p197": [197, 198, 199, 200, 201, 202, 203, 204],
"jild5-p204": [204, 205, 206, 207, 208, 209],
"jild5-p210": [210, 211],
"jild5-p211": [211, 212, 213, 214, 215],
"jild5-p215": [215, 216],
"jild5-p216": [216, 217, 218, 219, 220, 221],
"jild5-p221": [221, 222],
"jild5-p222": [222, 223, 224, 225, 226, 227, 228],
"jild5-p228": [228, 229, 230, 231, 232, 233],
"jild5-p233": [233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244],
"jild5-p244": [244, 245, 246],
"jild5-p246": [246, 247],
"jild5-p247": [247, 248, 249, 250, 251, 252, 253],
"jild5-p253": [253, 254, 255, 256, 257, 258, 259],
"jild5-p259": [259],
"jild5-p260": [260, 261],
"jild5-p262": [262, 263, 264, 265],
"jild5-p266": [266, 267, 268, 269, 270],
"jild5-p271": [271, 272, 273, 274, 275],
"jild5-p275": [275, 276, 277, 278, 279, 280, 281, 282, 283, 284],
"jild5-p285": [285, 286, 287, 288],
"jild5-p289": [289, 290],
"jild5-p291": [291, 292, 293, 294],
"jild5-p295": [295, 296, 297, 298, 299, 300, 301],
"jild5-p302": [302, 303, 304, 305, 306, 307, 308, 309],
"jild5-p310": [310, 311, 312, 313, 314],
"jild5-masala-287": [314, 315],
"jild5-masala-288": [315, 316],
"jild5-masala-289": [316, 317, 318, 319],
"jild5-masala-290": [320, 321],
"jild5-masala-292": [321, 322],
"jild5-masala-297": [323, 324],
"jild5-masala-298": [324, 325],
"jild5-masala-299": [325],
"jild5-masala-300": [325, 326],
"jild5-masala-301": [326],
"jild5-masala-302": [326, 327],
"jild5-masala-303": [327],
"jild5-masala-304": [328, 329],
"jild5-masala-305": [329, 330],
"jild5-masala-306": [330],
"jild5-masala-307": [330, 331],
"jild5-masala-308": [331],
"jild5-masala-309": [331],
"jild5-masala-310": [332],
"jild5-masala-311": [332],
"jild5-masala-312": [332, 333],
"jild5-masala-313": [333, 334],
"jild5-masala-314": [334, 335],
"jild5-masala-315": [335, 336, 337, 338, 339],
"jild5-masala-316": [339, 340, 341, 342],
"jild5-masala-317": [343, 344],
"jild5-masala-318": [344, 345],
"jild5-masala-319": [344, 345],
"jild5-masala-320": [345, 346],
"jild5-masala-321": [346],
"jild5-masala-322": [346, 347],
"jild5-masala-323": [347, 348, 349, 350, 351, 352, 353, 354, 355, 357, 358, 359, 360],
"jild5-masala-324": [361, 362, 363],
"jild5-masala-325": [363, 364, 365],
"jild5-masala-326": [365, 366],
"jild5-masala-327": [366, 367, 368],
"jild5-masala-328": [368, 369],
"jild5-masala-329": [370],
"jild5-masala-330": [370],
"jild5-masala-331": [370],
"jild5-masala-332": [370, 371],
"jild5-masala-333": [371, 372],
"jild5-masala-334": [372, 373],
"jild5-masala-335": [373],
"jild5-masala-336": [373, 374, 375, 376],
"jild5-masala-337": [376, 377],
"jild5-masala-338": [377, 378],
"jild5-masala-339": [378],
"jild5-masala-340": [378, 379],
"jild5-masala-341": [379],
"jild5-masala-342": [379],
"jild5-masala-343": [379],
"jild5-masala-344": [379, 380, 381, 382],
"jild5-masala-345": [382, 383, 384],
"jild5-masala-346": [384],
"jild5-masala-347": [384, 385, 386],
"jild5-masala-348": [386],
"jild5-masala-349": [386, 387],
"jild5-masala-350": [387, 388, 389],
"jild5-masala-351": [389, 390],
"jild5-masala-352": [390, 391, 392, 393, 394, 395, 396],
"jild5-masala-353": [396, 397],
"jild5-masala-354": [397],
"jild5-masala-455": [397, 398],
"jild5-p399": [399, 400, 401, 402, 403, 404],
"jild5-masala-356": [404],
"jild5-masala-357": [404, 405],
"jild5-masala-358": [406, 407, 408],
"jild5-masala-359": [408, 409],
"jild5-masala-360": [409, 410, 411, 412, 413],
"jild5-masala-361": [413],
"jild5-masala-263-p413": [413, 414],
"jild5-masala-364": [414],
"jild5-masala-366": [414, 415],
"jild5-masala-367": [415],
"jild5-masala-368": [415, 416, 417],
"jild5-masala-369": [417, 418],
"jild5-masala-370": [417, 418],
"jild5-masala-371": [418],
"jild5-masala-372": [419],
"jild5-masala-373": [419],
"jild5-masala-374": [419, 420],
"jild5-masala-375": [420],
"jild5-masala-376": [420, 421],
"jild5-masala-377": [421],
"jild5-masala-378": [421],
"jild5-masala-379": [421, 422],
"jild5-masala-380": [422, 423],
"jild5-masala-381": [423, 425],
"jild5-masala-382": [425],
"jild5-masala-383": [425, 426, 427],
"jild5-masala-304-p427": [427],
"jild5-masala-385": [427, 428],
"jild5-masala-386": [429, 430, 431, 432, 433, 434, 435, 436],
"jild5-p436": [436, 437, 438, 439, 440, 441, 442, 443],
"jild5-p443": [443, 444, 445, 447, 448, 449],
"jild5-p449": [449, 450, 451],
"jild5-p451": [451, 452],
"jild5-p452": [452, 453, 454],
"jild5-p454": [454, 455],
"jild5-p455": [455, 456],
"jild5-p456": [456, 457],
"jild5-p457": [457, 458, 459, 460, 461],
"jild5-p461": [461, 462, 463, 464, 465, 466, 467, 468, 469],
"jild5-p469": [469, 470, 471, 472, 473],
"jild5-p473": [473, 474, 475],
"jild5-p475": [475, 476],
"jild5-p476": [476, 477],
"jild5-p476b": [476, 477, 478],
"jild5-p478": [478],
"jild5-p479": [479, 480, 481, 482],
"jild5-p482": [482, 483, 484, 485, 487, 488],
"jild5-p488": [488, 489, 490, 491],
"jild5-p491": [491, 492, 493, 494, 495, 496],
"jild5-p496": [496, 497, 498, 499, 500, 501, 502, 503],
"jild5-p503": [503, 504, 506, 507],
"jild5-p507": [507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524],
"jild5-p524": [524, 525, 526, 527],
"jild5-p527": [527, 528],
"jild5-p529": [529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540],
"jild5-p540": [540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551],
"jild5-p551": [551, 552, 553, 554],
"jild5-p554": [554, 555, 556, 557, 558],
"jild5-p558": [558, 559, 560, 561, 562, 563, 564],
"jild5-p564": [564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574],
"jild5-p574": [574, 575, 576, 577],
"jild5-p577": [577, 578],
"jild5-p579": [579, 580, 581, 582],
"jild5-p583": [583, 584, 585],
"jild5-p585": [585, 586, 587, 588],
"jild5-p589": [589, 590, 591, 592, 593, 594, 595, 596, 597],
"jild5-p598": [598],
"jild5-p598-2": [598, 599, 600],
"jild5-p600": [600, 601, 602, 603],
"jild5-p603": [603, 604],
"jild5-p604": [604, 605, 606],
"jild5-p606": [606, 607],
"jild5-p608": [608, 609, 610, 611, 612, 613, 614, 615, 616, 617],
"jild5-p617": [617, 618],
"jild5-p619": [619, 620, 621, 622, 623],
"jild5-p623": [623, 624, 625, 626, 627, 628, 629, 630],
"jild5-masala-387": [631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654],
"jild5-masala-388": [655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 678, 679, 680],
"jild5-p681": [681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694],
}

# The Urdu word for "page" is safha; the canonical marker is [safha N].
# Lenticular brackets are U+3010 (open) and U+3011 (close); the short
# form is "[safha-initial N]" with the single-letter abbreviation.
# All three patterns are built from escapes so this file never contains
# a literal lenticular-bracket pair.
SAFHA = "\u0635\u0641\u062d\u06c1"  # the Urdu word for page
RE_LENTICULAR = re.compile("\u3010" + SAFHA + " (\\d+)\u3011")
RE_SHORT = re.compile("\\[\u0635 (\\d+)\\]")
RE_FULL = re.compile("\\[" + SAFHA + " \\d+\\]")
LENTICULAR_PREFIX = "\u3010" + SAFHA  # for the "none remain" check
SHORT_PREFIX_RE = re.compile("\\[\u0635 \\d+\\]")

# Canonical output key order for every item (the JSON contract).
ITEM_KEYS = ["id", "title", "volume_id", "pages", "start_page",
             "tashreeh_sawal", "tashreeh_jawab", "notes"]


def normalise_markers(text):
    """Normalise page markers in one string. Returns (new_text, counts)."""
    counts = {"lenticular": 0, "short": 0, "full_before": 0}
    counts["full_before"] = len(RE_FULL.findall(text))
    text, n1 = RE_LENTICULAR.subn("[" + SAFHA + " \\1]", text)
    counts["lenticular"] = n1
    text, n2 = RE_SHORT.subn("[" + SAFHA + " \\1]", text)
    counts["short"] = n2
    return text, counts


def normalise_item(item):
    """Normalise markers in every string field of one item (recursively
    through lists/dicts). Returns per-form counts for this item."""
    totals = {"lenticular": 0, "short": 0, "full_before": 0}

    def walk(value):
        if isinstance(value, str):
            new, c = normalise_markers(value)
            for k in totals:
                totals[k] += c[k]
            return new
        if isinstance(value, list):
            return [walk(v) for v in value]
        if isinstance(value, dict):
            return {k: walk(v) for k, v in value.items()}
        return value

    for key in list(item.keys()):
        item[key] = walk(item[key])
    return totals


def main():
    assert len(V3_IDS) == EXPECTED_ITEMS, "embedded V3_IDS length mismatch"
    assert set(V3_PAGES) == set(V3_IDS), "embedded V3_PAGES keys != V3_IDS"
    assert sum(len(v) for v in V3_PAGES.values()) >= EXPECTED_PAGES

    manifest = json.load(open(os.path.join(BASE, MANIFEST), encoding="utf-8"))
    entries = manifest["chunks"]
    assert len(entries) == 14, f"expected 14 manifest entries, got {len(entries)}"
    assert all(e.get("status") == "done" for e in entries), "not all chunks done"
    by_file = {e["file"]: e for e in entries}
    assert set(by_file) == set(CHUNK_ORDER), (
        f"manifest files != CHUNK_ORDER: "
        f"missing={set(CHUNK_ORDER) - set(by_file)} "
        f"extra={set(by_file) - set(CHUNK_ORDER)}"
    )

    all_items = []
    derived = []
    for fname in CHUNK_ORDER:
        path = os.path.join(BASE, fname)
        d = json.load(open(path, encoding="utf-8"))
        items = d["masail"]
        entry = by_file[fname]
        assert len(items) == entry["items"], (
            f"{fname}: {len(items)} items, manifest says {entry['items']}"
        )
        # Marker normalisation, with before/after counts per chunk.
        before = {"lenticular": 0, "short": 0, "full_before": 0}
        for it in items:
            c = normalise_item(it)
            for k in before:
                before[k] += c[k]
        after_full = sum(
            len(RE_FULL.findall(json.dumps(it, ensure_ascii=False)))
            for it in items
        )
        print(
            f"{fname}: {len(items)} items | markers before: "
            f"lenticular={before['lenticular']} short={before['short']} "
            f"full={before['full_before']} | after: full={after_full}"
        )
        assert after_full == (
            before["lenticular"] + before["short"] + before["full_before"]
        ), f"{fname}: marker count changed by normalisation!"
        # Derive start_page = min(pages) where absent (chunks 06, 12).
        for it in items:
            if "start_page" not in it:
                it["start_page"] = min(it["pages"])
                derived.append(it["id"])
        all_items.extend(items)

    # RENAME QUIRK (Jild 5 only): the book numbers TWO different masail
    # 263 and TWO different masail 304. The chunk files use the plain id
    # for both occurrences; the v3 merged file disambiguates the second
    # occurrences by appending the start page. Rename the SECOND
    # occurrence of any duplicated id to {id}-p{start_page}.
    seen_ids = set()
    renamed = []
    for it in all_items:
        if it["id"] in seen_ids:
            new_id = f"{it['id']}-p{min(it['pages'])}"
            renamed.append((it["id"], new_id))
            it["id"] = new_id
        seen_ids.add(it["id"])
    print(f"renames applied: {renamed}")
    assert renamed == [("jild5-masala-263", "jild5-masala-263-p413"),
                       ("jild5-masala-304", "jild5-masala-304-p427")], (
        f"unexpected renames: {renamed}"
    )

    print(f"concatenated: {len(all_items)} items")
    print(f"start_page derived for {len(derived)} items (expected 0: all chunks carry start_page)")
    assert len(all_items) == EXPECTED_ITEMS, (
        f"expected {EXPECTED_ITEMS} items, got {len(all_items)}"
    )

    # Rebuild each item in the canonical key order (the JSON contract).
    canonical = []
    for it in all_items:
        assert set(it.keys()) == set(ITEM_KEYS), (
            f"{it.get('id')}: keys {sorted(it.keys())} != {sorted(ITEM_KEYS)}"
        )
        canonical.append({k: it[k] for k in ITEM_KEYS})
    all_items = canonical

    # Validation.
    ids = [it["id"] for it in all_items]
    assert ids == V3_IDS, (
        f"ID sequence != v3: first diff at "
        f"{next((i for i, (a, b) in enumerate(zip(ids, V3_IDS)) if a != b), min(len(ids), len(V3_IDS)))}"
    )
    assert len(ids) == len(set(ids)), (
        f"DUPLICATE IDS: {[i for i in ids if ids.count(i) > 1]}"
    )
    empty = [it["id"] for it in all_items if not it.get("tashreeh_jawab")]
    assert not empty, f"EMPTY JAWAB: {empty}"
    vols = set(it.get("volume_id") for it in all_items)
    assert vols == EXPECTED_VOLUME_IDS, f"volume_ids {vols} != {EXPECTED_VOLUME_IDS}"
    pages = set()
    for it in all_items:
        assert it["pages"] == V3_PAGES[it["id"]], (
            f"{it['id']}: pages {it['pages']} != v3 {V3_PAGES[it['id']]}"
        )
        pages.update(it["pages"])
    assert len(pages) == EXPECTED_PAGES, (
        f"expected {EXPECTED_PAGES} unique pages, got {len(pages)}"
    )
    assert min(pages) == EXPECTED_MIN_PAGE, f"min page {min(pages)}"
    assert max(pages) == EXPECTED_MAX_PAGE, f"max page {max(pages)}"
    exceptions = {
        it["id"] for it in all_items if it["start_page"] != min(it["pages"])
    }
    assert not exceptions, f"start_page != min(pages): {sorted(exceptions)}"
    assert ids[0] == EXPECTED_FIRST_ID, f"first id {ids[0]}"
    assert ids[-1] == EXPECTED_LAST_ID, f"last id {ids[-1]}"

    out = {"masail": all_items}
    out_text = json.dumps(out, ensure_ascii=False, indent=1)
    assert LENTICULAR_PREFIX not in out_text, "lenticular markers remain in output!"
    assert not SHORT_PREFIX_RE.search(out_text), "short markers remain in output!"
    total_markers = len(RE_FULL.findall(out_text))
    print(
        f"VALIDATION PASSED: {len(all_items)} items, {len(pages)} unique pages "
        f"(min {min(pages)}, max {max(pages)}), volume_ids {sorted(vols)}, "
        f"first {ids[0]}, last {ids[-1]}, start_page == min(pages) for all, "
        f"derived start_page for {len(derived)} items, markers {total_markers}"
    )

    with open(os.path.join(BASE, "jild-05.json"), "w", encoding="utf-8") as f:
        f.write(out_text)
    print(f"WROTE jild-05.json: {len(out_text.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
