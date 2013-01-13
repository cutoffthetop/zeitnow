package zeitnow

import (
	"encoding/xml"
	"fmt"
	"net/http"
	"appengine"
	"appengine/urlfetch"
	"io/ioutil"
	)

func wikiWords(w http.ResponseWriter, r *http.Request) []string {
	type TrendingTopicsPage struct {
		Title	string	`xml:"title"`
		Id		string	`xml:"id"`
	}
	
	type TrendingTopics struct {
		XMLName	xml.Name 			 `xml:"pages"`
		Type	string				 `xml:"type,attr"`
		Page	[]TrendingTopicsPage `xml:"page"`
	}

	type WikiTranslation struct {
		XMLName	xml.Name	`xml:"api"`
		German	string		`xml:"query>pages>page>langlinks>ll"`
	}

	c := appengine.NewContext(r)
	client := urlfetch.Client(c)

	resp, _ := client.Get("http://www.trendingtopics.org/pages.xml")
	body, _ := ioutil.ReadAll(resp.Body)
	resp.Body.Close()

	result := TrendingTopics{}
	xml.Unmarshal([]byte(body), &result)

	var words []string = make([]string, len(result.Page))

	for i := range result.Page {

		url := "http://en.wikipedia.org/w/api.php?action=query&titles=" +
			result.Page[i].Title + "&prop=langlinks&format=xml&llcontinue=" +
			result.Page[i].Id + "|de&lllimit=1"

		translation := WikiTranslation{}
		resp, _ := client.Get(url)
		body, _ := ioutil.ReadAll(resp.Body)
		resp.Body.Close()

		xml.Unmarshal([]byte(body), &translation)

		words[i] = translation.German
	}

	return words
}

func init() {
	http.HandleFunc("/", handler)
}

func handler(w http.ResponseWriter, r *http.Request) {
	ww := wikiWords(w, r)
	for i := range ww {
		fmt.Fprintf(w, "%v\n", ww[i])
	}
}
