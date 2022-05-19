let easyTotal = 0;
let mediumTotal = 0;
let hardTotal = 0;
let deadlyTotal = 0;
let searchResults = {};
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

async function processNameAddForm(evt) {
    evt.preventDefault()

    let name = $('#monster-name').val()
    let data = {name: name}
    let resp = await axios.post('/encounter/add-name', data)
    $('.warning').remove()
    if (resp.data.errors) {
        showErrors('#monster-section', resp.data.errors)
    } else {
        let monster = resp.data[0]
        trackAndAppend(monster)
    } 
}

$('#monster-name-add-form').on('submit', processNameAddForm)

async function processSearchForm(evt) {
    evt.preventDefault()

    let cr = $('#monster-cr').val()
    let type = $('#monster-type').val()
    let data = {challenge_rating: cr, type: type}

    $('.warning').remove()
    $('#search-section').empty()
    loadingSpinner('#search-section')
    let resp = await axios.post('/encounter/search', data)
    endSpinner()
    if (resp.data.errors) {
        showErrors('#search-section', resp.data.errors)
    } else {
        searchResults = {...resp.data}
        populateSearchList(resp)
    }
}

function populateSearchList(resp) {
    $('#search-section').empty()

    for (let i = 0; i < resp.data.length; i++) {
        let monster = resp.data[i]
        let el = `<li class='p-2' data-slug='${monster.slug}'>${monster.name} - CR ${monster.challenge_rating}</li>`
        $('#search-section').append(el)
    }
}

function addFromSearch(evt) {
    let slug = $(evt.target).data('slug')
    let monster = {}

    for (let i in searchResults) {
        if (searchResults[i].slug === slug) {
            monster = {...searchResults[i]}
        }
    }
    trackAndAppend(monster)
}

$('#monster-search-form').on('submit', processSearchForm)
$('#search-section').on('click', 'li', addFromSearch)

function trackAndAppend(monster) {
    if (Object.keys(monsterTracker).indexOf(`${monster.slug}`) === -1) {    
        monsterTracker[`${monster.slug}`] = {}
        monsterTracker[`${monster.slug}`]['count'] = 1
        monsterTracker[`${monster.slug}`]['name'] = monster.name
        monsterTracker[`${monster.slug}`]['data'] = monster
        appendMonster(monster)
    } else {
        monsterTracker[`${monster.slug}`]['count'] += 1
        i = $(`h6:contains(${monster.name})`).data('id')
        getTitle(monsterTracker[`${monster.slug}`]['count'], i)
        getHp(monsterTracker[`${monster.slug}`]['data'].hit_points, monsterTracker[`${monster.slug}`]['count'], i)
    }
    
}

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

    let data = {
        difficulty: difficulty,
        density: density,
    }

    $('#monster-section').empty()
    loadingSpinner('#monster-section')
    let resp = await axios.post('/encounter/generate', data)
    endSpinner()
    if (resp.data.errors) {
        showErrors('#monster-section', resp.data.errors)
    } else {
        monsters = resp.data.monsters
        monsterTracker = {...monsters}
        clearMonsters()
        appendMonsters(monsters)
    }
}

async function updateCrs() {
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

    let data = {
        difficulty: difficulty,
        density: density
    }

    let resp = await axios.post('/encounter/calc-crs', data)
    let crCounter = resp.data
    printCrs(crCounter)
}

function printCrs(crCounter) {
    let el = $('#cr-section')
    el.empty()
    for (cr in crCounter) {
        el.append(` (${crCounter[cr]}x CR-${cr}) `)
    }
}

$('#parameters-form').on('submit', processParametersForm)
$('#enc-difficulty').on('change', updateCrs)
$('#density').on('change', updateCrs)

function removeMonster(evt) {
    let el = $(evt.target).parent()
    let slug = el.data('slug')
    let monster = monsterTracker[slug]['data']

    if (monsterTracker[slug]['count'] > 1) {
        monsterTracker[slug]['count'] -= 1
        i = $(`h6:contains(${monster.name})`).data('id')
        getTitle(monsterTracker[slug]['count'], i)
        getHp(monsterTracker[slug]['data'].hit_points, monsterTracker[slug]['count'], i)
    } else {
        delete monsterTracker[slug]
        el.remove()
    }
}

$('#monster-section').on('click', '.delete-btn', removeMonster)

function submitCreate() {
    if ($('#create-title').val() === '') {
        $('.footer-errors').text('Title required.')
    } else {
        let monsterRef = getRef(monsterTracker)
        $('#monsterRef').val(monsterRef)
        $('#create-form').submit()
    }
}

$('#create-btn').on('click', submitCreate)