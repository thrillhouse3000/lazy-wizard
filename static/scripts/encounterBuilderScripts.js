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
    updateCrs()
}

function addExpBudget(lvl) {
    easyTotal += encounterDifficulty[`${lvl}`].easy
    mediumTotal += encounterDifficulty[`${lvl}`].medium
    hardTotal += encounterDifficulty[`${lvl}`].hard
    deadlyTotal += encounterDifficulty[`${lvl}`].deadly
}

function subExpBudget(lvl) {
    easyTotal -= encounterDifficulty[`${lvl}`].easy
    mediumTotal -= encounterDifficulty[`${lvl}`].medium
    hardTotal -= encounterDifficulty[`${lvl}`].hard
    deadlyTotal -= encounterDifficulty[`${lvl}`].deadly
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
    $('.alert-danger').remove()
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

    $('.alert-danger').remove()
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

    let xp_total = 0
    if (selected === 'easy') {
        xp_total = easyTotal
    } else if (selected === 'medium') {
        xp_total = mediumTotal
    } else if (selected === 'hard') {
        xp_total = hardTotal
    } else {
        xp_total = deadlyTotal
    }

    let density = $('#density').val()

    let data = {
        xp_total: xp_total,
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
        $('#monster-section').empty()
        appendMonsters(monsters)
    }
}

async function updateCrs() {
    let selected = $('#enc-difficulty').val()

    let xp_total = 0
    if (selected === 'easy') {
        xp_total = easyTotal
    } else if (selected === 'medium') {
        xp_total = mediumTotal
    } else if (selected === 'hard') {
        xp_total = hardTotal
    } else {
        xp_total = deadlyTotal
    }

    let density = $('#density').val()

    let data = {
        xp_total: xp_total,
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
        el.append(` (CR-${cr}:  ${crCounter[cr]} ) `)
    }
}

$('#parameters-form').on('submit', processParametersForm)
$('#enc-difficulty').on('change', updateCrs)
$('#density').on('change', updateCrs)

function plusMonster(evt) {
    let el = $(evt.target).closest($('.card'))
    let slug = el.data('slug')
    let monster = monsterTracker[slug]['data']
    trackAndAppend(monster)
}

function subtractMonster(evt) {
    let el = $(evt.target).closest($('.card'))
    let slug = el.data('slug')
    let monster = monsterTracker[slug]['data']
    if (monsterTracker[slug]['count'] > 1) {
        monsterTracker[slug]['count'] -= 1
        i = $(`h6:contains(${monster.name})`).data('id')
        getTitle(monsterTracker[slug]['count'], i)
        getHp(monsterTracker[slug]['data'].hit_points, monsterTracker[slug]['count'], i)
    } else {
        return 
    }
}

function removeMonster(evt) {
    let el = $(evt.target).parent()
    let slug = el.data('slug')
    delete monsterTracker[slug]
    el.remove()
}

$('#monster-section').on('click', '#plus-btn', plusMonster)
$('#monster-section').on('click', '#minus-btn', subtractMonster)
$('#monster-section').on('click', '.delete-btn', removeMonster)

function createRef(callback) {
    let monsterRef = getRef(monsterTracker)
    $('#monsterRef').val(monsterRef)
    callback();
}

function submitCreate() {
    $('#create-form').submit()
}

async function createHandler() {
    if ($('#create-title').val() === '') {
        $('.footer-errors').text('Title required.')
    } else {
        createRef(submitCreate)
    }
}

$('#create-btn').on('click', createHandler)