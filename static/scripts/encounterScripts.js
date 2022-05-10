let easyTotal = 0;
let mediumTotal = 0;
let hardTotal = 0;
let deadlyTotal = 0;
let monsterTracker = {};

function pcLvlSubmit(evt) {
    evt.preventDefault()
    let lvl = $('#pc-lvl').val()
    $('#party').append(`<div class='party-icon d-inline-block mx-1 px-2'>Lvl ${lvl}</div>`)
    addExpBudget(lvl)
}

function addExpBudget(lvl) {
    easyTotal += encounterDifficulty[`${lvl}`].easy
    $('#easy-total').text(`Easy: ${easyTotal}`)
    mediumTotal += encounterDifficulty[`${lvl}`].medium
    $('#medium-total').text(`Medium: ${mediumTotal}`)
    hardTotal += encounterDifficulty[`${lvl}`].hard
    $('#hard-total').text(`Hard: ${hardTotal}`)
    deadlyTotal += encounterDifficulty[`${lvl}`].deadly
    $('#deadly-total').text(`Deadly: ${deadlyTotal}`)
}

function subExpBudget(lvl) {
    easyTotal -= encounterDifficulty[`${lvl}`].easy
    $('#easy-total').text(`Easy: ${easyTotal}`)
    mediumTotal -= encounterDifficulty[`${lvl}`].medium
    $('#medium-total').text(`Medium: ${mediumTotal}`)
    hardTotal -= encounterDifficulty[`${lvl}`].hard
    $('#hard-total').text(`Hard: ${hardTotal}`)
    deadlyTotal -= encounterDifficulty[`${lvl}`].deadly
    $('#deadly-total').text(`Deadly: ${deadlyTotal}`)
}

function removeCharacter(evt) {
    let el = $(evt.target)
    let lvl = el.text().slice(-1)
    el.remove()
    subExpBudget(lvl)
}

$('#pc-lvl-form').on('submit', pcLvlSubmit)
$('#party').on('click','.party-icon', removeCharacter)

async function processAddForm(evt) {
    evt.preventDefault()

    let name = $('#monster-name').val()

    if (Object.keys(monsterTracker).indexOf(name) === -1) {
        let data = {name: name}
        let resp = await axios.post('/encounter/add', data)
        let monster = resp.data[0]
        monsterTracker[`${monster.name}`] = {}
        monsterTracker[`${monster.name}`]['count'] = 1
        monsterTracker[`${monster.name}`]['data'] = monster
        appendMonster(monster)
    } else {
        monsterTracker[`${name}`]['count'] += 1
        i = $(`h5:contains(${name})`).data('id')
        getTitle(monsterTracker[`${name}`]['count'], i)
        getHp(monsterTracker[`${name}`]['data'].hit_points, monsterTracker[`${name}`]['count'], i)
    }
    
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

    let resp = await axios.post('/encounter/create', data)
    let monsters = resp.data.monsters
    monsterTracker = {...monsters}
    clearMonsters()
    appendMonsters(monsters)
}

$('#parameters-form').on('submit', processParametersForm)

function removeMonster(evt) {
    let el = $(evt.target).parent()
    let monsterName = el.find('h5').text()

    if (monsterTracker[monsterName]['count'] > 1) {
        monsterTracker[monsterName]['count'] -= 1
        i = $(`h5:contains(${monsterName})`).data('id')
        getTitle(monsterTracker[monsterName]['count'], i)
        getHp(monsterTracker[monsterName]['data'].hit_points, monsterTracker[monsterName]['count'], i)
    } else {
        delete monsterTracker[monsterName]
        el.remove()
    }
}

$('#monster-section').on('click', '.delete-btn', removeMonster)