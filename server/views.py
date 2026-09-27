"""Server-rendered account pages. No customer data or tokens in public assets."""
from html import escape
from server.coin_client import render_summary


def page(content):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow"><title>Your account — LazyingArt</title>'
        '<link rel="icon" href="/favicon.ico"><link rel="stylesheet" href="/styles.css">'
        '<link rel="stylesheet" href="/account.css"></head><body>'
        '<header class="header wrap"><a class="brand" href="/">'
        '<img src="/assets/panda-v1/logo-256.png" width="51" height="51" alt="">'
        '<span>LazyingArt</span></a><a href="/">Explore the tools</a></header>'
        '<main class="wrap account-main">'+content+'</main><footer class="wrap footer">'
        '<span>LazyingArt account</span><a href="/privacy.html">Privacy</a></footer></body></html>')


def sign_in(providers, csrf, *, message=''):
    labels = {'password':'Email','google':'Google','apple':'Apple','github':'GitHub'}
    content = '<section class="account-card"><p class="eyebrow">Your LazyingArt account</p><h1>A familiar way in.</h1>'
    if message:
        content += '<p role="status">'+escape(message)+'</p>'
    if providers:
        content += '<p>Sign in or create an account through EchoMind’s shared account service.</p>'
        content += '<p class="provider-list">'+escape(' · '.join(labels[p] for p in providers))+'</p>'
        content += '<form method="post" action="/api/account/start">'+csrf+'<button class="button">Continue to sign in or sign up</button></form>'
        content += '<p class="small">You choose your sign-in method on the account page. Your provider password never comes to this platform.</p>'
    else:
        content += '<p>Shared sign-in is not available here yet. Your existing apps still work.</p><a class="button" href="https://chat.lazying.art/login">Open EchoMind sign-in</a>'
    return content+'</section>'


def dashboard(identity, coin, csrf, *, can_connect=False, account_url=None, message=''):
    name = escape(identity.display_name or 'LazyingArt member')
    content = '<section class="account-heading"><p class="eyebrow">Your account</p><h1>'+name+'</h1><p>Signed in to LazyingArt.</p>'
    if message:
        content += '<p role="status">'+escape(message)+'</p>'
    content += '</section><div class="account-grid"><div class="account-card" data-testid="coin-summary">'
    if coin['state'] == 'available':
        content += render_summary(coin['summary'], identity)
    else:
        messages = {
            'not_connected':'LAC account summaries are not connected here yet.',
            'permission_required':'Choose whether to show your LAC summary on this platform.',
            'authorization_required':'Reconnect your Coin read permission to see your summary.',
            'rate_limited':'The Coin service is busy. Please try again shortly.',
            'temporarily_unavailable':'Your LAC summary is temporarily unavailable. Your balance has not been changed.',
        }
        content += '<h2>Your LAC</h2><p>'+messages.get(coin['state'],messages['temporarily_unavailable'])+'</p>'
        if can_connect and coin['state'] in ('permission_required','authorization_required'):
            content += '<p class="small">Read-only access to your linked wallet balance and grant history. This does not link accounts, move coins or grant spending rights.</p>'
            content += '<form method="post" action="/api/account/coin/connect">'+csrf+'<button class="button">Choose Coin read access</button></form>'
        content += '<p><a class="text-link" href="https://coin.lazying.art/">Open Coin ↗</a></p>'
    content += '</div><section class="account-card"><h2>Account &amp; access</h2>'
    if account_url:
        content += '<p><a class="text-link" href="'+escape(account_url,quote=True)+'">Manage your shared account ↗</a></p>'
    content += '<p>App access, purchases and EchoMind credits remain with each service. Signing in here does not make a purchase or claim an award.</p>'
    content += '<form method="post" action="/api/account/logout">'+csrf+'<input type="hidden" name="return_to" value="account"><button class="button outline">Sign out of this platform</button></form></section></div>'
    content += '<section class="account-tools"><h2>Pick up where you want to go</h2><div class="story-grid">'
    for label, url, description in (
        ('EchoMind','https://chat.lazying.art/','Conversations and language help.'),
        ('Bunko','https://lachlan.lazying.art/Bunko/','Classics with reading help alongside.'),
        ('AiMemo','https://aimemo.lazying.art/','A place for notes, tasks and ideas.'),
        ('OnlyIdeas','https://agent.onlyideas.art/','Papers, equations and questions.'),
    ):
        content += '<a class="story" href="'+url+'"><h3>'+label+'</h3><p>'+description+'</p><span class="text-link">Open '+label+' ↗</span></a>'
    return content+'</div><p class="small">Each app keeps its own workspace and may still ask you to sign in.</p></section>'
