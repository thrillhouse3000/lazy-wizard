function generateHtml(monster, i) {
    return `<div class="card mb-3 monster-card" data-slug='${monster.slug}'>
        <button class='me-0 btn btn-sm btn-danger delete-btn'>X</button>
        <div class="row" id='title-row'>
            <div class="col-lg-5">
                <div class="card-body">
                    <h6 class="card-text d-inline" id='monster-name-${i}' data-id='${i}'><b><span class='first-letter'>${monster.name[0]}</span>${monster.name.substring(1)}</b></h6>
                    <span id='monster-multiplier-${i}'></span>
                </div>
            </div>
            <div class="col-lg">
                <div class="card-body">
                    <button class='btn btn-sm btn-lw mx-2' id='plus-btn'>+</button>
                    <button class='btn btn-sm btn-lw mx-2' id='minus-btn'>-</button>
                </div>
            </div>>
        </div>  
        <div class="row g-0">
            <div class="col-lg-3">
                <div class="card-body">
                    <p class="card-text"><b>CR ${monster.challenge_rating}</b> ${monster.size} ${monster.type}, ${monster.alignment}</p>
                    <p class="card-text"><b>AC</b> ${monster.armor_class}</p>
                    <p class="card-text"><b>Speed</b> ${getSpeeds(monster.speed)}</p>
                    ${monster.languages ? `<p class="card-text"><b>Languages</b> ${monster.languages}</p>` : ''}
                </div>
            </div>
            <div class="col-lg-7">
                <div class="card-body">
                    <p class="card-text d-inline-block"><b>STR</b> ${monster.strength} (${getMod(monster.strength)})</p>
                    <p class="card-text d-inline-block"><b>DEX</b> ${monster.dexterity} (${getMod(monster.dexterity)})</p>
                    <p class="card-text d-inline-block"><b>CON</b> ${monster.constitution} (${getMod(monster.constitution)})</p>
                    <p class="card-text d-inline-block"><b>INT</b> ${monster.intelligence} (${getMod(monster.intelligence)})</p>
                    <p class="card-text d-inline-block"><b>WIS</b> ${monster.wisdom} (${getMod(monster.wisdom)})</p>
                    <p class="card-text d-inline-block"><b>CHA</b> ${monster.charisma} (${getMod(monster.charisma)})</p>
                    <p class="card-text"><b>Saves</b> ${getSaves([monster.strength_save, monster.dexterity_save, monster.constitution_save, monster.intelligence_save, monster.wisdom_save, monster.charisma_save])}</p>
                    <p class="card-text"><b>Senses</b> ${monster.senses}</p>
                    ${Object.keys(monster.skills).length ? `<p class="card-text"><b>Skills</b> ${getSkills(monster.skills)}</p>` : ''}
                    ${monster.damage_vulnerabilities ? `<p class="card-text"><b>Damage Vulnerabilities</b> ${monster.damage_vulnerabilities}</p>` : ''}
                    ${monster.damage_resistances ? `<p class="card-text"><b>Damage Resistances</b> ${monster.damage_resistances}</p>` : ''}
                    ${monster.damage_immunities ? `<p class="card-text"><b>Damage Immunities</b> ${monster.damage_immunities}</p>` : ''}
                    ${monster.condition_immunities ? `<p class="card-text"><b>Condition Immunities</b> ${monster.condition_immunities}</p>` : ''}
                </div>
            </div>
            <div class="col-lg-2">
                <div class="card-body text-center" id='hp-${i}'>
                </div>
            </div>
        </div>
        <div class="row">
            <div class="col">
                <div class="card-body">
                    <p class="card-text" id="actions-${i}"><b>Actions</b></p>
                    ${monster.reactions ? `<p class="card-text" id='reactions-${i}'><b>Reactions</b></p>` : ''}
                    ${monster.legendary_desc ? `<p class="card-text"><b>Legendary</b> ${monster.legendary_desc}</p>` : ''}
                    ${monster.legendary_actions ? `<p class="card-text" id="legendary-actions-${i}"><b>Legendary Actions</b></p>` : ''}
                    ${monster.special_abilities ? `<p class="card-text" id="special-abilities-${i}"><b>Special Abilities</b></p>` : ''}
                    ${monster.spell_list.length ? `<p class="card-text" id="spell-list-${i}"><b>Spells</b></p>` : ''}
                </div>
            </div>
        </div>
    </div>`
}

function appendMonsters(monsters) {
    keys = Object.keys(monsters)
    for (let i = 0; i < keys.length; i++) {
        el = generateHtml(monsters[`${keys[i]}`]['data'], i)
        $('#monster-section').append(el)
        getStats(monsters[`${keys[i]}`]['data'], i)
    }
    enablePopovers()
}

function appendMonster(monster) {
    $('#monster-section').children().length === 0 ? i = 0 : i = $('#monster-section').children().length + 1
    let el = generateHtml(monster, i)
    $('#monster-section').append(el)
    getStats(monster, i)
    enablePopovers()
}

function getStats(monster, i) {
    getTitle(monsterTracker[`${monster.slug}`]['count'], i)
    getHp(monster.hit_points, monsterTracker[`${monster.slug}`]['count'], i)
    getFeatures(monster.actions, '#actions', i)
    getFeatures(monster.reactions, '#reactions', i)
    getFeatures(monster.legendary_actions, '#legendary-actions', i)
    getFeatures(monster.special_abilities, '#special-abilities', i)
    getSpells(monster.spell_list, i)
}

function getTitle(count, i) {
    if (count > 1) {
        $(`#monster-multiplier-${i}`).empty()
        let multiplier = `<h6 class="card-title d-inline">(x${count})</h6>`
        $(`#monster-multiplier-${i}`).append(multiplier) 
    } else {
        $(`#monster-multiplier-${i}`).empty()
    }
}

function getHp(monsterHp, count, i) {
    $(`#hp-${i}`).empty()
    for (let j = 0; j < count; j++) {
        let el = `<p class='hp-block'><b>HP</b> ${j+1}:  <input type='text' value='${monsterHp}' style='width: 2rem;'> / ${monsterHp}</p>`
        $(`#hp-${i}`).append(el)
    }
}

function getMod(num) {
    let mod = Math.floor((num - 10)/2)
    if (mod >= 0) {
        return `+${mod}`
    } else {
        return `${mod}`
    }
}

function getSpeeds(arr) {
    let str = ''
    for (speed in arr) {
        str += `${speed}: ${arr[speed]} `
    }
    return str
}

function getSaves(arr) {
    let str = ''
    for (save in arr) {
        if (arr[save] !== null){
            if (save === '0') {
                str += `STR +${arr[save]} `
            } else if (save === '1') {
                str += `DEX +${arr[save]} `
            } else if (save === '2') {
                str += `CON +${arr[save]} `
            } else if (save === '3') {
                str += `INT +${arr[save]} `
            } else if (save === '4') {
                str += `WIS +${arr[save]} `
            } else if (save === '5') {
                str += `CHA +${arr[save]} `
            }
        }
    }
    if (str === '') {
        return 'No proficiencies'
    } else {
        return str
    }
}

function getSkills(skillsObj) {
    let str = ''
    for (skill in skillsObj) {
        str += `${skill} +${skillsObj[skill]} `
    }
    return str
}

function getFeatures(feature, targetEl, i) {
    for (let item in feature) {
        let el = $(`<a tabindex="0" class='mx-1 feature' role="button" data-bs-toggle="popover" data-bs-container="body" data-bs-trigger="focus" title="${feature[item]['name']}" data-bs-content="${feature[item]['desc']}">${feature[item]['name']}</a>`)
        $(`${targetEl}-${i}`).append(el)
    }
}

async function getSpells(spellsArr, i) {
    let data = {};
    if (spellsArr.length) {
        for (let j = 0; j < spellsArr.length; j++) {
            data[`${j}`] = spellsArr[j]
        }
        loadSpellSpinner(`#spell-list-${i}`)
        let resp = await axios.post('/encounter/spells', data)
        endSpellSpinner()
        appendSpells(resp.data, i)
    }
    enablePopovers()
}

function generateSpellHtml(spell) {
    return `<a tabindex="0" class='mx-1 feature' role="button" data-bs-toggle="popover" data-bs-container="body" data-bs-trigger="focus" title="${spell.name}" data-bs-content="${spell.desc}">${spell.name}</a>`
}

function appendSpells(spellsObj, i) {
    let keys = Object.keys(spellsObj)
    for (let j = 0; j < keys.length; j++) {
        let el = generateSpellHtml(spellsObj[j])
        $(`#spell-list-${i}`).append(el)
    }
}

function updateRef() {
    monsterRef = {}
    for (let monster in monsterTracker) {
        monsterRef[monsterTracker[`${monster}`].name] = `${monsterTracker[monster].count}`
    }
    $('#monsterRef').val(JSON.stringify(monsterRef))
}

function loadingSpinner(el){
    $(el).append('<div class="lds-dual-ring" id="spinner"></div>')
}

function endSpinner() {
    $('#spinner').remove();
}

function loadSpellSpinner(el){
    $(el).append('<div class="spell-dual-ring" id="spell-spinner"></div>')
}

function endSpellSpinner() {
    $('#spell-spinner').remove();
}

function showErrors(targetEl, errors) {
    for (let error in errors) {
        let el = `<div class="alert alert-danger alert-dismissible fade show text-center" style='text-shadow: none;' role="alert">
                    <span>${errors[error]}</span>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>`
        $(targetEl).append(el)
    }
}

function setMaxHeightSearch() {
    if ($(window).width() > 991) {
        let remainingHeight = $(window).height() - ($('#party-div').height() + $('#generate-encounter-div').height() + $('#search-form-div').height() + $('#calc-cr-div').height() + $('footer').height() + 60)
        $('.search-div').css({'max-height': remainingHeight})
    } else {
        $('.search-div').css({'max-height': '20vh'})
    }
}

function setMaxHeightMonsters() {
    if ($(window).width() > 991) {
        let remainingHeight = $(window).height() - ($('.monster-header').height() + $('footer').height() + 64)
        $('#monster-section').css({'max-height': remainingHeight})
    } else {
        $('#monster-section').css({'max-height': 'none'})
    }
}

setMaxHeightSearch()
setMaxHeightMonsters()
$(window).on('resize', setMaxHeightSearch)
$(window).on('resize', setMaxHeightMonsters)

function enablePopovers() {
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))
    const popover = new bootstrap.Popover('.popover-dismiss', {
        trigger: 'focus'
      })
}

