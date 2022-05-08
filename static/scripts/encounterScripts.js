let easyTotal = 0;
let mediumTotal = 0;
let hardTotal = 0;
let deadlyTotal = 0;

function pcLvlSubmit(evt) {
    evt.preventDefault()
    let lvl = $('#pc-lvl').val()
    $('#party').append(`<span>Lvl ${lvl}</span>`)
    updateExpBudget(lvl)
}

function updateExpBudget(lvl) {
    easyTotal += encounterDifficulty[`${lvl}`].easy
    $('#easy-total').text(`Easy: ${easyTotal}`)
    mediumTotal += encounterDifficulty[`${lvl}`].medium
    $('#medium-total').text(`Medium: ${mediumTotal}`)
    hardTotal += encounterDifficulty[`${lvl}`].hard
    $('#hard-total').text(`Hard: ${hardTotal}`)
    deadlyTotal += encounterDifficulty[`${lvl}`].deadly
    $('#deadly-total').text(`Deadly: ${deadlyTotal}`)
}

$('#pc-lvl-form').on('submit', pcLvlSubmit)

async function processAddForm(evt) {
    evt.preventDefault()

    let name = $('#monster-name').val()

    let data = {name: name}

    resp = await axios.post('/encounter/add', data)
    clearAndAppendMonster(resp.data)
}

$('#monster-add-form').on('submit', processAddForm)

async function processParametersForm(evt) {
    evt.preventDefault()
    let selected = $('#enc-difficulty').val()

    let difficulty = 0
    if (selected === 'easy') {
        difficulty = easyTotal
    } else if (selected === 'medium') {
        difficulty = mediumTotal
    } else if (selected === 'hard') {
        difficulty = hardTotal
    } else {
        difficulty = deadlyTotal
    }

    let density = $('#density').val()
    let type = $('#type').val()
    let terrain  = $('#terrain').val()

    let data = {
        difficulty: difficulty,
        density: density,
        type: type,
        terrain: terrain
    }

    resp = await axios.post('/encounter/create', data)
    clearAndAppendMonster(resp.data)
}

$('#parameters-form').on('submit', processParametersForm)

function generateHtml(monster, i) {
    return `<div class="card mb-3 w-100">
        <div class="row g-0">
            <div class="col-3">
                <div class="card-body">
                    <h5 class="card-title">${monster.name}</h5>
                    <p class="card-text"><b>CR ${monster.challenge_rating}</b> ${monster.size} ${monster.type}, ${monster.alignment}</p>
                    <p class="card-text"><b>AC</b> ${monster.armor_class}</p>
                    <p class="card-text"><b>Speed</b> ${getSpeeds(monster.speed)}</p>
                    ${monster.languages ? `<p class="card-text"><b>Languages</b> ${monster.languages}</p>` : ''}
                </div>
            </div>
            <div class="col-8">
                <div class="card-body">
                    <p class="card-text d-inline"><b>STR</b> ${monster.strength} (${getMod(monster.strength)})</p>
                    <p class="card-text d-inline"><b>DEX</b> ${monster.dexterity} (${getMod(monster.dexterity)})</p>
                    <p class="card-text d-inline"><b>CON</b> ${monster.constitution} (${getMod(monster.constitution)})</p>
                    <p class="card-text d-inline"><b>INT</b> ${monster.intelligence} (${getMod(monster.intelligence)})</p>
                    <p class="card-text d-inline"><b>WIS</b> ${monster.wisdom} (${getMod(monster.wisdom)})</p>
                    <p class="card-text d-inline"><b>CHA</b> ${monster.charisma} (${getMod(monster.charisma)})</p>
                    <p class="card-text"><b>Saves:</b> ${getSaves([monster.strength_save, monster.dexterity_save, monster.constitution_save, monster.intelligence_save, monster.wisdom_save, monster.charisma_save])}</p>
                    <p class="card-text"><b>Senses</b> ${monster.senses}</p>
                    ${Object.keys(monster.skills).length ? `<p class="card-text"><b>Skills:</b> ${getSkills(monster.skills)}</p>` : ''}
                    ${monster.damage_vulnerabilities ? `<p class="card-text"><b>Damage Vulnerabilities</b> ${monster.damage_vulnerabilities}</p>` : ''}
                    ${monster.damage_resistances ? `<p class="card-text"><b>Damage Resistances</b> ${monster.damage_resistances}</p>` : ''}
                    ${monster.damage_immunities ? `<p class="card-text"><b>Damage Immunities</b> ${monster.damage_immunities}</p>` : ''}
                    ${monster.condition_immunities ? `<p class="card-text"><b>Condition Immunities</b> ${monster.condition_immunities}</p>` : ''}
                </div>
            </div>
            <div class="col">
                <div class="card-body">
                    <p class="card-text">HP: ${monster.hit_points}</p>
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

function clearAndAppendMonster(obj) {
    $('#monster-section').empty()
    keys = Object.keys(obj)
    for (let i = 0; i < keys.length; i++) {
        el = generateHtml(obj[i], i)
        $('#monster-section').append(el)
        getActions(obj[i].actions, i)
        getReactions(obj[i].reactions, i)
        getLegendaryActions(obj[i].legendary_actions, i)
        getSpecialAbilities(obj[i].special_abilities, i)
        getSpells(obj[i].spell_list, i)
    }
}

function getMod(num) {
    mod = Math.floor((num - 10)/2)
    if (mod >= 0) {
        return `+${mod}`
    } else {
        return `${mod}`
    }
}

function getSpeeds(arr) {
    str = ''
    for (speed in arr) {
        str += `${speed}: ${arr[speed]} `
    }
    return str
}

function getSaves(arr) {
    str = ''
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

function getSkills(obj) {
    str = ''
    for (skill in obj) {
        str += `${skill} +${obj[skill]} `
    }
    return str
}

function getActions(obj, i) {
    for (let action in obj) {
        let el = ` <a href="#" data-bs-toggle="tooltip" data-bs-placement="top" title="${obj[action]['desc']}">${obj[action]['name']}</a>`
        $(`#actions-${i}`).append(el)
    }
}

function getReactions(obj, i) {
    for (let action in obj) {
        let el = ` <a href="#" data-bs-toggle="tooltip" data-bs-placement="top" title="${obj[action]['desc']}">${obj[action]['name']}</a>`
        $(`#reactions-${i}`).append(el)
    }
}

function getLegendaryActions(obj, i) {
    for (let action in obj) {
        let el = ` <a href="#" data-bs-toggle="tooltip" data-bs-placement="top" title="${obj[action]['desc']}">${obj[action]['name']}</a>`
        $(`#legendary-actions-${i}`).append(el)
    }
}

function getSpecialAbilities(obj, i) {
    for (let ability in obj) {
        let el = ` <a href="#" data-bs-toggle="tooltip" data-bs-placement="top" title="${obj[ability]['desc']}">${obj[ability]['name']}</a>`
        $(`#special-abilities-${i}`).append(el)
    }
}

async function getSpells(obj, i) {
    data = {};
    if (obj.length) {
        for (let j = 0; j < obj.length; j++) {
            data[`${j}`] = obj[j]
        }
        resp = await axios.post('/encounter/spells', data)
        appendSpells(resp.data, i)
    }
}

function generateSpellHtml(spell) {
    return ` <a href="#" data-bs-toggle="tooltip" data-bs-placement="top" title="${spell.desc}">${spell.name}</a>`
}

function appendSpells(obj, i) {
    keys = Object.keys(obj)
    for (let j = 0; j < keys.length; j++) {
        let el = generateSpellHtml(obj[j])
        $(`#spell-list-${i}`).append(el)
    }
}