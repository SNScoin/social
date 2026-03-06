require('dotenv').config();
const axios = require('axios');

(async () => {
    try {
        console.log('Sending ScrapeNinja request...');
        const res = await axios.post('https://scrapeninja.p.rapidapi.com/scrape', {
            url: 'https://www.instagram.com/reel/DAz-65qMHyi/',
            render: true,
            wait: 3000
        }, {
            headers: {
                'x-rapidapi-key': process.env.RAPIDAPI_KEY,
                'x-rapidapi-host': 'scrapeninja.p.rapidapi.com',
                'Content-Type': 'application/json'
            }
        });

        const html = res.data.body;
        console.log('HTML Length:', html.length);

        const titleMatch = html.match(/<title>(.*?)<\/title>/);
        console.log('Title:', titleMatch ? titleMatch[1] : 'NOT FOUND');

        const descMatch = html.match(/<meta[^>]*name=\"description\"[^>]*content=\"([^\"]*)\"[^>]*>/);
        const fbDescMatch = html.match(/<meta[^>]*property=\"og:description\"[^>]*content=\"([^\"]*)\"[^>]*>/);

        console.log('Meta Desc:', descMatch ? descMatch[1] : 'NOT FOUND');
        console.log('OG Desc:', fbDescMatch ? fbDescMatch[1] : 'NOT FOUND');

        const likeMatch = html.match(/([\d,]+)\s*likes/);
        console.log('Likes Regex:', likeMatch ? likeMatch[1] : 'NOT FOUND');

    } catch (e) {
        console.error('err', e.message);
    }
})();
