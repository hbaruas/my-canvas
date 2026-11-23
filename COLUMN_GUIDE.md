Hey — sorry for the slightly delayed reply, wanted to actually look into all of this properly rather than give you a half answer.

On retailer first — it's not that prices are holding anything back. There's a field called selling_business already sitting in the data we've been using the whole time — it lists Trainline, TfL, Ctrip alongside the actual train operators, so retailer-type information does exist, it's just never made it into anything I've published so far since the original ask was always region and time, not retailer. Worth me knowing though — were you looking at my output specifically, or a fuller list from somewhere else? If it's the latter there might be a genuinely different thing missing that I haven't spotted, so don't want to assume it's the same field until I know what you were looking at.

On whether it'd need a full resend if they did send something extra — genuinely no idea, that's not something I can answer from anything I've got, it'd need asking of whoever manages the access side of things.

On the zone fields and the destination question — this took a bit of digging but I think I've got a proper answer now rather than a guess. The zone fields (dest_primary_zone and dest_secondary_zone) turned out to be fare zones, similar to how Travelcard areas work, with only a handful of distinct values between them — so they were never going to tell us where anyone actually went, they're about pricing areas, not places. The field that looks like it should give us a real destination, destination_code, has thousands of distinct values, which looked promising at first. Except when I went back through some earlier profiling we'd done on this data, one of the most common values in it is "LONDON BR," which just means "could be any of several London termini" — and that happens specifically because season tickets get recorded as valid to a whole zone rather than one actual stop. Which is awkward, because season tickets are exactly the ticket type this commuting question is about. So the field goes vague precisely where we need it to be precise, and I don't think there's a clean station-level answer sitting there waiting to be used.

I also want to flag something on the "just filter by operator" idea, since I think that's a natural next thought and it's worth being upfront about why it doesn't quite work either. fields like that tell us which channel sold or processed the ticket, not which network the journey actually ran on — and separately, we already know TfL-tagged activity in this data is overwhelmingly contactless/PAYG tap activity rather than purchased tickets, which is a different thing from knowing which network someone actually travelled on. Some of those same "TfL" rows are genuinely ordinary National Rail journeys that just happened to be paid for that way. So dropping everything tagged TfL wouldn't just remove Underground trips, it'd remove real rail activity too, and we'd have no way of knowing how much of each we'd just thrown out.

Now, the actually useful bit — you'd pointed me at that ORR quality report a while back and I hadn't got round to reading it properly, which I've now done, and it's genuinely helpful. The headline thing is that ORR's own published rail figures already exclude London Underground entirely — they say so directly, their mainline numbers don't include Eurostar, Underground, light rail, or heritage/charter services. So someone's already solved this properly, which is reassuring on its own.

How they do it is the useful part. It's not a destination or geography trick at all. Apparently LENNON holds two different internal datasets — a "pre-allocation" one, which is basically raw ticket sales by route and doesn't know which specific operator a journey belongs to, and a "post-allocation" one, where that's been resolved down to actual named operators. ORR build their figures from the post-allocation side specifically, because that's the one where a journey can be properly attributed to an operator — and London Underground just never receives anything that way, since it isn't part of that revenue-sharing system at all. So it's excluded structurally, not filtered out after the fact.

Which leaves an obvious, specific question for us: is what we've been pulling the pre-allocation version or the post-allocation version? I don't know yet, and I don't want to guess either way properly, but one small thing nudges me toward suspecting we might be on the pre-allocation side — their own worked example of a pre-allocation entry is a ticket booked "ANY PERMITTED" between London Terminals and Birmingham, and "ANY PERMITTED" happens to be the single most common value in route_desc in what we've got, at about a quarter of the whole table. Not proof, just enough of a hint that it's worth actually asking rather than assuming.

If it turns out we've got the operator-resolved version available, this stops being a proxy problem and becomes something much cleaner. If we haven't, we're not worse off than before, just better informed about why this has been genuinely hard rather than us missing something obvious.

One more thing worth saying honestly — even ORR's own numbers aren't spotless on this. They describe a known issue where contactless/PAYG journeys in London can get counted more than once when there's more than one possible route for a single tap, and they say plainly they've only specifically fixed that for one line (the Elizabeth line, using a separate dataset straight from TfL) rather than everywhere. So even in the best case here, I think this gets us a lot closer rather than perfectly clean.






Hi Andrew,

Thanks for this, and sorry for not getting back sooner, wanted to look into things properly rather than reply quickly.

On the double-counting point with Katherine's check — I don't have anything useful to add there myself, no visibility into how that estimate is put together, so I'll leave that one with her rather than guess at it.

On the TfL proxy idea Joel and I have been discussing — there's a simple version, excluding journeys that start and end in London, and that's straightforward, buildable from what we've already got whenever it's wanted. I did also look at a more precise version using a finer destination field instead of just the region, and I want to be upfront that it's turned out weaker than I first thought rather than just needing more checking. Going back through some earlier profiling of this data, that finer field goes vague specifically for season tickets — it ends up recording something like "could be any of several London stations" rather than one actual stop, and that's exactly the ticket type this commuting question is about. So I don't want to promise that version is close to sorted. There's a specific question I want to put to the data team that should tell us whether it's salvageable at all, and between that and a few other things I've got on, I'd rather be honest that I can't give this a date yet than suggest it's further along than it is.

Happy to take a look at the shading on the regional matrix in the meantime — that one I can just get on with, no dependencies there.

On seasonality — I want to give you an honest answer rather than a polished one. There was something early on in this data that looked like it might be seasonal, but it was never properly confirmed, and it comes from the very first month this dataset has any coverage at all, so I genuinely can't tell "this is seasonal" apart from "the data was still ramping up." So the honest position is we don't know yet whether it's seasonal, not that we've seen it and chosen not to adjust for it. Happy to look into that properly if it's something you'd want ahead of RTI, just didn't want to guess at an answer I don't actually have.

I'll follow up once I've heard back from the data team on the destination field question.

Best,
Saurabh

I'll go ask the pre/post-allocation question. Can't promise how quickly I'll hear back, got a couple of other things on at the moment, but it feels like the one thing worth actually asking rather than us continuing to poke at it from our end.
